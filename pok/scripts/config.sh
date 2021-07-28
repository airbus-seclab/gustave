#!/bin/bash
export ROOT=$(git rev-parse --show-toplevel)/pok
source "${ROOT}/.gustave.env"
${ROOT}/config/__pok_gen_config.py
