(c) Airbus 2020, sduverger

# POK Memory filtering bitmap

## Introduction

This is the POK memory map generator to fasten up memory filtering
during fuzzing. The purpose of this tool is to provide a bitmap to
GUSTAVE so that it can filter on memory accesses during fuzzing
without too much overhead.

We thought about exposing legitimate memory areas through:

- javascript conf file ranges list, to build up a linked list at
  runtime
- hashtable (glib or gperf)
- a raw bitmap

POK physical memory space is 2^32. With 1 bit per byte, we can define
a `bitmap` for every physical memory byte. The map occupies
500MB. This is acceptable and allows for O(1) accesses during memory
filtering.

This bitmap is a shared memory for several GUSTAVE instances
initialized only once. It remains resident until `shm_unlink`.

## Generating the filter bitmap

The following examples are related to POK firmware images built
*without* AFL shims. Code coverage for AFL is done at QEMU TCG
level. Building POK in *src* mode generates slightly bigger firmware
images and require dedicated filtering bitmap.

Do not forget to add valid memory range for code coverage bitmap:
- `0xe0000000 0x10000` for PPC
- `0x80000000 0x10000` for x86

These are MMIO range where the target kernel injected shims update
code coverage information for AFL. In TCG mode, this is done inside
QEMU and thus does not need exclusion from filtering bitmap.

The gustave JSON configuration file exposes these ranges through
`afl-trace-addr` and `afl-trace-size` parameters. The coverage bitmap
size depends on AFL. The default value is 64KB.

When trying different filtering bitmaps, take care to unlink SHM with
`./mem_ranges/unlink_bitmap`, as it is resident.

### Intel x86

POK allocates kernel from `0x100000`. The partition areas (gdt
segments) are allocated from the heap and their kernel stack too. The
user stacks are located inside partition's segments. We just have to
collect the last heap addr as an acceptable over approximation.

After a simple run of the POK firmware in QEMU (without GUSTAVE) we
obtain the following output. The firmware is built for x86
architecture and does not include AFL shim at build time:

```
HEAP end |0x32c8e0|
Partition 0 base=|220000| size=|10c8e0|
HEAP end |0x32e8e0|
Partition 0 kstack=|32c8e0| size=|2000|
HEAP end |0x33ac30|
Partition 1 base=|32e8e0| size=|c350|
HEAP end |0x33cc30|
Partition 1 kstack=|33ac30| size=|2000|
HEAP end |0x33dc30|
POK kernel initialized
```

The *valid* memory range being `[0x00100000 - 0x0033dc2f]`.

We simply create fake log files for each 'arch/mode' and run
`mmranges.py` tool to generate its binary representation. The log
files pattern format is text `tag start size`, such as `wmm 0x100000
0x23dc30`.

The `mmranges.py` tool is provided as is, trivial, simple/stupid to
ease excluding memory ranges. We could have used a shell one-liner to
generate the basic POK filter bitmaps.


### PowerPC

POK for PPC enables MMU for user partitions. They run at virtual
address 0. The kernel memory space is running at `0x80000000` but
physically loaded as a ROM at `0xfff00000` (ie. last 1MB) for the
code/rodata and from `0x10000` for rwdata:

```
$ readelf -e pok.elf
 [ 1] .text     PROGBITS     fff00000 010000 008f38 00  AX
 [ 2] .rodata   PROGBITS     fff08f38 018f38 0ac8f8 00  WA
...
 [ 5] .data     PROGBITS     00010000 0d0000 000058 00  WA
 ...
 [ 9] .reset    PROGBITS     fffffffc 0dfffc 000004 00  AX
...
 LOAD  0x010000 0xfff00000 0xfff00000 0xb5830 0xb5830 RWE 0x10000
 LOAD  0x0d0000 0x00010000 0xfffb5830 0x06444 0x06444 RW  0x10000
 LOAD  0x0dfffc 0xfffffffc 0xfffffffc 0x00004 0x00004 R E 0x10000
```

As for x86, we retrieve runtime userland physical memory mappings:

```
HEAP end |0xb4b10|
Partition 0 base=|16000| size=|9eb10|
pok_create_space: id 0 base 16000 sz 9eb10
HEAP end |0xb7000|
space_context_create 0: entry=80458 stack=9cb60 arg1=dead arg2=beaf ksp=b6fa0
HEAP end |0xd44c0|
Partition 1 base=|b7000| size=|1d4c0|
pok_create_space: id 1 base b7000 sz 1d4c0
HEAP end |0xd7000|
space_context_create 1: entry=454 stack=1b510 arg1=dead arg2=beaf ksp=d6fa0
HEAP end |0xd8000|
ctxt_create 5: sp=d7f98
POK kernel initialized
```

We can thus manually create (slightly) over-approximated memory ranges
for addresses manipulated by the kernel:

```
[0xfff00000 - 0xfffb5830] kernel code
[0x00010000 - 0x00016000] kernel data
[0x00016000 - 0x000d8000] physical addr for partitions
[0xfffffffc - 0xffffffff] reset vector
```

Giving us the following input file to generate a bitmap:

```
rwmm 0x00010000 0xc8000
rwmm 0xfff00000 0xb5830
rwmm 0xfffffffc 0x4
```


## Generating another memory log file (and bitmap)

We already provide a bitmap but if you want to build one, proceed as
follows:

```
T> make logmem
T> ./scripts/run.sh > /tmp/mm.log 2>&1
```

Once the system has reached an interesting point, stop qemu. And then
generate a new bitmap:

```
T1> cd mem_ranges
T1> grep '[wr]mm' /tmp/mm.log > rw.trace
T1> sort -k 2 rw.trace > rw.trace.sorted
T1> ./mmranges.py rw.trace.sorted

T1> ls rw.trace.sorted*
rw.trace.sorted
rw.trace.sorted.ranges
rw.trace.sorted.bitmap
```

## Testing filter bitmap

The accessed memory binary file structure is as follows:

```
target_ulong ranges[][2];
```

POK is a 32bits system so `target_ulong` is `uint32_t`. The generated
file is little-endian (as host architecture, x86 in our case).

```
mmranges.py  ::  parses QEMU log file to create binary file.
bitmap.c     ::  generates the bitmap in SHM and tests it.
```

The `bitmap` tool creates a SHM if it does not exist and wait. Any
subsequent calls to `bitmap` will behave as client and only read the
bitmap.

```
T1> make
T1> ./bitmap rw.trace.sorted.bitmap

shm_open(rdonly) ... try create: No such file or directory
create shm
[...]
parsed bitmap

T2> ./bitmap

<addr>

T1> ^C
unlink shm
```
