#!/bin/bash

#
# Launch multiple intances of GUSTAVE managed by tmux
#

## Prepare environment
export ROOT=$(git rev-parse --show-toplevel)/pok
source "${ROOT}/.gustave.env"

## Proceed with some AFL checks
AFL_CHECKS=1
source "${ROOT}/scripts/check"

## Starts tmux session
tmux new-session -d -s gustave-pok

# Spwan AFL
TARGET="${QRUN}"
for n in $(grep processor /proc/cpuinfo | cut -d':' -f2)
do
    nr=$(printf "%02d" ${n})

    if [ $nr == "00" ];then
	cmd="${AFL} -M -- ${TARGET}"
    else
	cmd="${AFL} -S ${nr} -- ${TARGET}"
    fi

    echo $cmd > /tmp/afl.cmd.${nr}
    tmux new-window -d "${cmd}"
done
tmux attach
