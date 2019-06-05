# GUSTAVE - Embedded OS kernel fuzzer

## What is it ?

GUSTAVE is a fuzzing platform for embedded OS kernels. It is based on
QEMU and AFL (and all of its *forkserver* siblings). It allows to fuzz
OS kernels like simple applications.

Thanks to QEMU, it is multi-platform. One can see GUSTAVE as a AFL
*forkserver* implementation inside QEMU, with fine grain target
inspection.

## What are the supported kernels ?

GUSTAVE has mainly been designed to target embedded OS kernels. It
might not be the best tool to fuzz a large and complex Windows or
Linux kernel.

However if you have a target under the hood which can be rebuilt from
scratch and crafted with one or two applications to boot without any
user interaction, it might be interesting to give GUSTAVE a try.


## How does it work ?

The `afl-fuzz` tool, from the AFL project, is used to automatically
fuzz your target. However, AFL can't directly fuzz an OS kernel and
expects its target to directly parse the generated test cases.

To make it short, `afl-fuzz` will run QEMU with GUSTAVE integration as its
target. In turn, GUSTAVE will handle :
- forkserver synchronization
- generated test cases translation to target system calls
- target kernel monitoring

## How does it compare to existing solutions ?

There exists comparable approaches, such as:
- [Project Triforce](https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2016/june/project-triforce-run-afl-on-everything/)
- [afl-unicorn](https://hackernoon.com/afl-unicorn-fuzzing-arbitrary-binary-code-563ca28936bf)
- [kAFL](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-schumilo.pdf)

GUSTAVE design choices implies the following differences:
- you need to inject AFL instrumentation shims in the target kernel
- no specific devs are needed inside the target
- really **target agnostic** (OS, architecture), as long as QEMU offers support
- can even use *hardware-virtualization* with kvm
- covers **all system calls** implemented in the target kernel
- you still need to implement target specific things:
  - system calls translator
  - memory guard oracles

## Current status ?

### Hardware

We have implemented and tested **Intel x86** and **PowerPC** support.
The GUSTAVE implementation is architecture independent. If you can run
your target with QEMU, you can fuzz it with GUSTAVE with little
effort.

For now, we provide example Intel 440FX and PowerPC PREP boards with
GUSTAVE integration. The implementation of your own board is really
easy. Have a look at [x86 board](https://github.com/airbus-seclab/qemu/blob/gustave/hw/i386/fuzz/afl.c).

We also added support for x86 and PowerPC GUSTAVE instrumentation
shims to **afl-gcc**.


### Software

We also provide [POK](https://pok-kernel.github.io/) micro-kernel
target specific developments:

- system call ABI generator for both x86/PPC
- x86 memory oracles


## How to use it ?

- prepare your target (rebuild with `afl-gcc`, or binary fix it)
- implement target specific translator
- build QEMU with GUSTAVE integration
- write a JSON configuration file for your target
- run it in a terminal

A step-by-step [tutorial](doc/README.md) is available.

### Requirements

Beside a working compilation environment for both your target and
QEMU, you will need the following `git` trees:

```bash
$ git clone -b gustave https://github.com/airbus-seclab/afl
$ git clone -b gustave https://github.com/airbus-seclab/qemu
```

## Publications

Material from different talks on GUSTAVE can be found at
https://airbus-seclab.github.io/. English slides are available
[here](https://airbus-seclab.github.io/GUSTAVE_thcon/GUSTAVE_thcon.pdf).
