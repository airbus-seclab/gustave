#!/bin/bash

#
# Launch single intance of GUSTAVE
#

## Prepare environment
export ROOT=$(git rev-parse --show-toplevel)/pok
source "${ROOT}/.gustave.env"

## Proceed with some AFL checks
AFL_CHECKS=1
source "${ROOT}/scripts/check"

# Spwan AFL
TARGET="${QRUN}"
cmd="${AFL} -- ${TARGET}"
$cmd
