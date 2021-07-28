#!/bin/bash
export ROOT=$(git rev-parse --show-toplevel)/pok
source "${ROOT}/.gustave.env"
$GDB -ex "file ${POK_VM}/pok.elf" -x $GDB_SCRIPT
