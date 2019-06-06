# Getting GUSTAVE up & running

## Building AFL

You need to rebuild `afl-gcc/afl-as` because we provide specific shims to access
the coverage map through arbitrary mmio.

Notice that the default `afl-fuzz` config file `config.h` has been
fixed for:

```c
#define EXEC_TIMEOUT        3000

#ifndef __x86_64__
#  define MEM_LIMIT         1025
#else
#  define MEM_LIMIT         1050
#endif /* ^!__x86_64__ */
```

### Intel x86
```bash
$ make
```

### PowerPC PREP

```bash
$ AFL_NO_X86=1 make
```

## Building your TARGET

You are on your own on this. But here are some hints:

- fix toolchain to wrap your compiler at interesting part (kernel code)
- override `CC` to call `afl-gcc` instead of original compiler
- define `AFL_CC` and `AFL_AS` with original compiler/assembler

## Building QEMU

The [QEMU project documentation](https://github.com/qemu/qemu) already
provides a lot of details.

You may have differents needs (vnc, curses, sdl). But below are
working command lines.

### Intel x86

```bash
$ ./configure --target-list=i386-softmmu --enable-debug --enable-curses --enable-sdl
```

### PowerPC PREP

```bash
$ ./configure --target-list=ppc-softmmu --disable-user
--disable-sdl --disable-tpm --disable-libxml2 --disable-cap-ng
--disable-curses --disable-vnc --disable-blobs --disable-kvm
--disable-guest-agent
```

## Running GUSTAVE

On a dedicated terminal, get board and target logging

```bash
$ tail -f /tmp/qemu.*
```

On another dedicated terminal (*dark colors strongly advised by AFL*),
start fuzzing with a target configuration JSON file.

You can find example ones in [conf](/conf)

```bash
$ afl-fuzz <afl_opts> -- qemu-system-xxx <qemu_opts> -M afl -gustave <target.json>
```

## Troubleshooting GUSTAVE

### Prevent AFL binary check

```bash
$ export AFL_SKIP_BIN_CHECK=1
```

AFL looks into target strings for `__AFL_SHM_ID`, its default coverage
bitmap environment variable name.

However, AFL's target will be QEMU and the variable name is given
through the JSON configuration file, so it will never find it into the
executable file.


### Accelerate `calibrate_test_case()`.

```bash
$ export AFL_FAST_CAL=1
```

### Core pattern

```bash
$ echo core >/proc/sys/kernel/core_pattern
```

To prevent

```bash
[-] Hmm, your system is configured to send core dump notifications to an
    external utility. This will cause issues: there will be an extended delay
    between stumbling upon a crash and having this information relayed to the
    fuzzer via the standard waitpid() API.

    To avoid having crashes misinterpreted as timeouts, please log in as root
    and temporarily modify /proc/sys/kernel/core_pattern, like so:

    echo core >/proc/sys/kernel/core_pattern

[-] PROGRAM ABORT : Pipe at the beginning of 'core_pattern'
         Location : check_crash_handling(), afl-fuzz.c:7275

```


### Create AFL `in/out` directories

To prevent

```bash
[-] The input directory does not seem to be valid - try again. The fuzzer needs
    one or more test case to start with - ideally, a small file under 1 kB
    or so. The cases must be stored as regular files directly in the input
    directory.

[-]  SYSTEM ERROR : Unable to open '/tmp/afl_in'
    Stop location : read_testcases(), afl-fuzz.c:1435
       OS message : No such file or directory
```


### Put initial test case in AFL `in` directory

To prevent

```bash
[-] Looks like there are no valid test cases in the input directory! The fuzzer
    needs one or more test case to start with - ideally, a small file under
    1 kB or so. The cases must be stored as regular files directly in the
    input directory.

[-] PROGRAM ABORT : No usable test cases in '/tmp/afl_in'
         Location : read_testcases(), afl-fuzz.c:1496
```

### Cleanup your `/tmp`

After a lot of *try-and-die*, you may have remaining `afl-vmstate.*`
files holding snapshots of the target. You can remove them.