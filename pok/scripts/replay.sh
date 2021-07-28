#!/bin/bash

#
# Launch replay mode Gustave (no AFL)
#
if [ $# -lt 1 ];then
    echo "missing argument: <crash_test_case_file>" ; exit 1
fi

## Prepare environment
export ROOT=$(git rev-parse --show-toplevel)/pok
source "${ROOT}/.gustave.env"

## Proceed with some checks
source "${ROOT}/scripts/check"

## Spwan Gustave
TARGET="${QRUN} -s"
test_case=$1 ; shift
# allow remaining qemu args
echo
echo "  . You can connect with './scripts/gdb.sh'"
echo "  . Check logs with 'tail -f /tmp/qemu.err.0'"
$TARGET $* < $test_case
