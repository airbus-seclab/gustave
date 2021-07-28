#!/bin/bash

## Prepare environment
export ROOT="$(git rev-parse --show-toplevel)/pok"
source "${ROOT}/.gustave.env"

## clear afl session
(cd /tmp ; rm -rf afl.cmd.* gdb.* qemu.* afl-vmstate.* afl_out/*)

## remove shm filtering bitmap
${ROOT}/mem_ranges/unlink_bitmap
