(c) Airbus 2021, sduverger

# GUSTAVE for POK (x86 && PPC)

This repository provides runtime environment for fuzzing POK kernel
with GUSTAVE simulating a x86 or PPC board.

## Requirements

You need a building environment and tools:
```
T> sudo apt install gcc-multilib make binutils-multiarch tmux
```

If you want to try POK for PPC:
```
T> sudo apt install binutils-powerpc-linux-gnu gcc-powerpc-linux-gnu gdb-multiarch
```

## Directory tree

```
config/            - holds ready-to-use config and tool
input/             - basic input to start fuzzing with
output/            - sample fuzzing sessions
mem_ranges/        - memory filter bitmap builder/check
scripts/           - helps you run GUSTAVE
```

## Building

```
T> make
	 (c) Gustave Embedded OS kernel fuzzer

usage: make <fast|debug|replay>

    fast   : no debug, long term fuzzing sessions
    debug  : full debug log (testcase, injected code)
    replay : debug a crash case


T> make debug
```

This will build POK, AFL and QEMU with GUSTAVE in debug mode. Have a
look at the `Makefile` to check for retrieved git repositories.

## Memory filtering bitmap

GUSTAVE implements a memory filter bitmap to check for illegal
accesses during fuzzing. Have a look at `mem_ranges/README.md`.


## Configuration file

You can find samples in `./config` or you can regenerate an
appropriate one using:

```
T> ./scripts/config.sh
```

Some configuration values still have to be retrieved from runtime
environment, such as physical memory location of attacker partition,
or heap memory top.

Take care that there exists absolute path inside the configuration
file for:

- `conf["vm-state-template"]`, template for vm snapshot file
- `conf["vm-mem-ranges"]`    , path to memory filter bitmap

## Fuzzing POK

```
T> ls scripts/
afl_tmux.sh  afl.sh check  cleanup.sh  config.sh  env.sh  gdb.sh  replay.sh  run.sh

T> ./scripts/afl_tmux.sh
```

The provided scripts check for environment settings and files. Anyway,
*almost sure is not sure*, you should ensure that config file is
reachable and memory filtering bitmap too.

The script launches a tmux session with as much AFL instances as you
have available cpu cores. The `afl.sh` script is a single core variant
without tmux.

Log files, snapshots and crash cases are generated in `/tmp`:

```
T> ls -l /tmp
 afl.cmd.xxx
 afl_in/
 afl_out/
 pok_ranges.bin
 qemu.err.xxx
 qemu.out.xxx
```

The filtering bitmap shared memory is resident even if you kill
GUSTAVE. This is not a problem. It will be reused next time you launch
it.

If you want to change/update the filtering bitmap, use
`./mem_ranges/unlink_bitmap`.

If you want to purge `/tmp/` use `./scripts/cleanup.sh`.


## Replaying crash case


### Rebuild GUSTAVE

You need to rebuild GUSTAVE in `replay mode`:

```
T> make replay
```

After that you will be able to replay a given AFL crash case:

```
T> ./scripts/replay.sh '/path/to/test.case'
```

## TMUX tips

```
tmux attach         to get back to a lost session
<ctl b w>           list windows
<ctl b d>           detach from session
tmux kill-session   destroy everything
```
