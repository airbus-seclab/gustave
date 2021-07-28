#!/bin/bash
export ROOT=$(git rev-parse --show-toplevel)/pok
source "${ROOT}/.gustave.env"
TARGET="${QRUN}"
$TARGET
