(c) Airbus 2021, sduverger

# GUSTAVE - Embedded OS kernel fuzzer

## What is it ?

GUSTAVE is a fuzzing platform for embedded OS kernels. It is based on
[QEMU](https://www.qemu.org/) and
[AFL](https://lcamtuf.coredump.cx/afl/) (and all of its *forkserver*
siblings). It allows to fuzz OS kernels like simple applications.

Thanks to QEMU, it is multi-platform. One can see GUSTAVE as a AFL
*forkserver* implementation inside QEMU, with fine grain target
inspection.

## What are the supported kernels ?

GUSTAVE has mainly been designed to target embedded OS kernels. It
might not be the best tool to fuzz large and complex kernels as found
in Windows, Linux or MACOS.

However if you have a target under the hood which can be prepared with
one or two applications to boot without any user interaction, it might
be interesting to give GUSTAVE a try.

## How does it work ?

The `afl-fuzz` tool, from the AFL project, is used to automatically
fuzz your target. However, AFL can't directly fuzz an OS kernel and
expects its target to directly parse the generated test cases.

To make it short, `afl-fuzz` will run QEMU with GUSTAVE integration as its
target. In turn, GUSTAVE will handle :
- forkserver synchronization
- generated test cases translation to target system calls
- target kernel monitoring (execution coverage and memory accesses)

As AFL/QEMU-user mode found in
[AFL++](https://github.com/AFLplusplus/AFLplusplus) project, GUSTAVE
implements QEMU TCG IR level binary instrumentation for code coverage.

However, you can choose to disable it and rebuild your target kernel
code with only specific parts being subject to code coverage
analysis. You will have to inject AFL shims at build time to update
the trace bitmaps though. That was our initial approach (see
[Publications](#publications)).

Less prevalent in existing solutions, GUSTAVE does not care about
monitoring `kernel panics`. We consider them managed errors, and want
to discover illegal behaviors that did not trigger any alarm.

For that purpose GUSTAVE relies on a O(1) byte oriented memory
filtering bitmap to detect *illegal* accesses from the kernel. There
might be large debate about defining what could be considered illegal
from the kernel point of view. But in restricted embedded, highly
deterministic environments you might find yourself comfortable
defining *legitimate* memory areas for your firmware and tracking
out-of-bound accesses.

## How does it compare to existing solutions ?

There exists comparable approaches, such as:
- [PowerFL](https://www.petergoodman.me/docs/qpss-2019-slides.pdf)
- [Project Triforce](https://www.nccgroup.trust/us/about-us/newsroom-and-events/blog/2016/june/project-triforce-run-afl-on-everything/)
- [afl-unicorn](https://hackernoon.com/afl-unicorn-fuzzing-arbitrary-binary-code-563ca28936bf)
- [kAFL](https://www.usenix.org/system/files/conference/usenixsecurity17/sec17-schumilo.pdf)

GUSTAVE design choices imply the following differences:
- really **target agnostic** (OS, architecture), as long as QEMU
  offers support
- covers **all system calls** implemented in the target kernel
- no specific devs are needed inside the target

However, you still need to tell GUSTAVE:
- how your target handles system calls
- what is your target legitimate memory layout

## Current status ?

### Host hardware

For now only x86 host is supported, as many working environments are
based upon this architecture we don't consider it a prohibiting
limitation.

The restriction comes from the way we initially implemented memory
filtering backend at `tcg-target` level for the QEMU load/store
fast-path. The recent `TCGPlugin` memory callbacks architecture might
be an alternative approach to support any host.

### Guest Hardware

We have implemented and tested *Intel x86* and *PowerPC* support. The
GUSTAVE implementation is architecture independent. If you can run
your target with QEMU, you can fuzz it with GUSTAVE with little
effort.

We provide example [Intel
440FX](https://github.com/airbus-seclab/qemu/blob/gustave/hw/i386/gustave/afl.c)
and [PowerPC
PREP](https://github.com/airbus-seclab/qemu/blob/gustave/hw/ppc/gustave/afl.c)
boards with GUSTAVE integration. The implementation of your own board
is really easy, and consist in wrapping the `MACHINE_INIT` function
for a given architecture.

We also added support for x86 and PowerPC GUSTAVE instrumentation
shims to `afl-gcc`, in case you don't want to proceed with TCG binary
instrumentation.

### Example target

We provide [POK](https://pok-kernel.github.io/) micro-kernel specific
developments:

- firmware with simple applications
- system calls ABI generator for both x86/PPC
- filtering bitmap


## How to use it ?

You will need to:
- build AFL
- build QEMU with GUSTAVE integration
- create or generate the filtering bitmap
- write a JSON configuration file for your target
- run it in a terminal

Read [the manual](pok/README.md) for the POK target.


## Publications

Material from different talks on GUSTAVE can be found at
https://airbus-seclab.github.io/.
