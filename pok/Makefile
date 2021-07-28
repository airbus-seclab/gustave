#!/usr/bin/make -f
.SILENT:
.PHONY: afl pok mem_ranges qemu fast debug replay logmem
SHELL=/bin/bash

export ROOT=$(shell git rev-parse --show-toplevel)/pok
env=.gustave.env
include $(env)

gitremote=https://github.com/airbus-seclab
gitbranch=gustave

help:
	echo -ne "\n\t (c) Gustave Embedded OS kernel fuzzer\n"
	echo -ne "\nusage: make <fast|debug|replay>\n\n"
	echo -ne "    fast   : no debug, long term fuzzing sessions\n"
	echo -ne "    debug  : full debug log (testcase, injected code)\n"
	echo -ne "    replay : debug a crash case\n\n"

$(QEMU_PATH):
	git clone $(gitremote)/qemu -b $(gitbranch) $@

$(AFL_PATH):
	git clone $(gitremote)/afl -b $(gitbranch) $@

$(POK_PATH):
	git clone $(gitremote)/pok -b $(gitbranch) $@

$(env):
	echo -e "\n ! Missing environment, please use './scripts/env.sh'\n"
	exit 1

check: $(env)

mem_ranges:
	make -C $@

afl: $(AFL_PATH)
	(make -C "${AFL_PATH}" clean ; exit 0)
	make -C "${AFL_PATH}"

pok: $(POK_PATH)
	make -C "${POK_VM}"

deps: check afl pok mem_ranges pok

fast: deps
	TARGET_MODE=-DAFL_MODE_FUZZ_FAST make qemu
debug: deps
	TARGET_MODE=-DAFL_MODE_FUZZ_DEBUG make qemu
replay: deps
	TARGET_MODE=-DAFL_MODE_CRASH_CASE_REPLAY make qemu
logmem: deps
	TARGET_MODE="-DAFL_MODE_DISABLED -DMEM_FILTER -DMEM_FILTER_DEBUG" make qemu
run: deps
	TARGET_MODE="-DAFL_MODE_DISABLED" make qemu

ifneq ($(TARGET_MODE),)
EXFLG=$(subst ",,$(TARGET_MODE)) $(subst ",,$(QFLG))
QEMU_CONF=$(subst ",,$(QBLD)) --extra-cflags='$(EXFLG)'

qemu: $(QEMU_PATH)
	([ ! -d ${QEMU_BUILD} ] && mkdir ${QEMU_BUILD}) ; cd ${QEMU_BUILD} && ([[ ! -e config.status || -z "$$(grep -e '${EXFLG}' config.status)" ]] && ../configure ${QEMU_CONF}) ; make -j64

endif
