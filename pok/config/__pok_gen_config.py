#!/usr/bin/env python
import json, sys, struct, os

conf = {
    "user-timeout": 3000,
    "qemu-overhead": 10,
    "vm-state-template": "/tmp/afl-vmstate.XXXXXX",
    "afl-control-fd": 198,
    "afl-status-fd": 199,
    "afl-trace-size": 65536,
    "afl-trace-env": "__AFL_SHM_ID",
    "afl-trace-addr": 0,
    "vm-part-base": 0,
    "vm-part-size": 0,
    "vm-part-off": 0,
    "vm-nop-size": 0,
    "vm-fuzz-inj": 0,
    "vm-size": 0,
    "vm-part-kstack": 0,
    "vm-part-kstack-size": 0,
    "vm-fuzz-ep": 0,
    "vm-fuzz-ep-next": 0,
    "vm-panic": 0,
    "vm-cswitch": 0,
    "vm-cswitch-next": 0
}

# Kernel and partition files from pok firmware repo
repo=os.getenv("POK_VM")
arch=os.getenv("POK_ARCH")
cov=os.getenv("AFL_POK_COV")

if arch is None or repo is None or cov is None:
    sys.stderr.write("""
 !!! missing environment ! launch './scripts/config.sh'

""")
    sys.exit(1)

architectures = ["x86", "ppc"]
if not arch in architectures:
    sys.stderr.write("unsupported architecture: %s\n" % (arch))
    sys.exit(1)

coverages = ["src", "tcg"]
if not cov in coverages:
    sys.stderr.write("unsupported coverage mode: %s\n" % (cov))
    sys.exit(1)

kernel = repo+"/pok.elf"
part   = repo+"/part1/part1.elf"

#
# Static parameters
#
if arch == "x86":
    nop_tag = "<main>:"
    conf["afl-trace-addr"] = 0x80000000
    conf["vm-nop-size"] = 0x100000

    # declared kernel/deployment.h: 1100000 (base 10)
    conf["vm-part-size"] = 1100000

    # run-time retrieved: cf. mmranges.py
    if cov == "tcg":
        # Values for TCG mode
        conf["vm-size"] = 0x33dc30
        conf["vm-part-base"] = 0x220000
    elif cov == "src":
        # Values for SRC mode
        conf["vm-size"] = 0x355030
        conf["vm-part-base"] = 0x242350

    conf["vm-part-kstack"] = 0x32c8e0
    conf["vm-part-kstack-size"] = 8192

###### PPC
elif arch == "ppc":
    nop_tag = "<thr_job>:"
    conf["afl-trace-addr"] = 0xe0000000
    conf["vm-nop-size"] = 0x20000*4
    conf["vm-part-size"] = 650000
    conf["vm-part-base"] = 0x16000

    # not tested for PPC
    conf["vm-size"] = 0
    conf["vm-part-kstack"] = 0
    conf["vm-part-kstack-size"] = 0

else:
    sys.stderr.write("unsupported arch: %s\n" % (arch))
    sys.exit(1)

sys.stderr.write("""
VM-PART-BASE = 0x%08x
VM-SIZE      = 0x%08x

These will be runtime configured values ! Check before running GUSTAVE !'
""" % (conf["vm-part-base"], conf["vm-size"]))




def get_addr_from_objdump(line):
    return int(line.split(':')[0].strip(),16)

def find_stack_switch(line):
    if arch == "x86" and "(%esp),%esp" in l:
        return True

    if arch == "ppc" and "r1,r4" in l:
        return True

    return False

#
# Look at pok_fatal symbol
#
cmdline = "grep pok_fatal %s.map" % (kernel)
tmp = os.popen(cmdline).readlines()
if len(tmp) < 1:
    sys.stderr.write("can't find kernel panic\n")
    sys.exit(1)

panic = int(tmp[0].strip().split()[0],16)
conf["vm-panic"] = panic

#
# Look at context switch function. The idea is to break right after
# switching kernel stack.
#
# In the following example at '0x1108d2' for i386 arch
#
#  1108c0 <pok_context_switch>:
#  1108c0:       9c                      pushf  
# [...]
#  1108ce:       8b 64 24 34             mov    0x34(%esp),%esp
#  1108d2:       61                      popa   
# [...]
#
#
# In the following example at '0xfff24ebc' for ppc arch
#
#  fff24e54 <pok_context_switch>:
#  fff24e54:	7c 08 02 a6 	mflr    r0
# [...]
#  fff24ebc:	7c 81 23 78 	mr      r1,r4
#  fff24ec0:	83 e1 00 58 	lwz     r31,88(r1)
# [...]
#  fff24ec8:	83 a1 00 50 	lwz     r29,80(r1)

cmdline = "objdump -d %s | grep -A30 '<pok_context_switch>:'" % (kernel)
tmp = os.popen(cmdline).readlines()
if len(tmp) < 10:
    sys.stderr.write("can't find pok_switch_context (1)\n")
    sys.exit(1)

step=0
for l in tmp:
    if step == 1:
        switch=get_addr_from_objdump(l)
        step = 2
    elif step == 2 :
        switch_next=get_addr_from_objdump(l)
        break
    elif find_stack_switch(l):
        step = 1

if step != 2:
    sys.stderr.write("can't find pok_switch_context (2)\n")
    sys.exit(1)

conf["vm-cswitch"] = switch
conf["vm-cswitch-next"] = switch_next


#
# Look into partition 1, target partition to inject code into
# Partition base
# Partition offset
#

cmdline = "objdump -d %s | grep '%s'" % (part,nop_tag)
tmp = os.popen(cmdline).readlines()
if len(tmp) < 1:
    sys.stderr.write("can't find vm partition offset\n")
    sys.exit(1)

# 'bl 4' for PPC and 'endbr32' for x86
conf["vm-part-off"] = int(tmp[0].strip().split()[0],16) + 4
conf["vm-fuzz-inj"] = conf["vm-part-base"] + conf["vm-part-off"]

if arch == "x86":
    conf["vm-fuzz-ep"] = conf["vm-fuzz-inj"]
    conf["vm-fuzz-ep-next"] = conf["vm-fuzz-ep"] + 1
elif arch == "ppc":
    conf["vm-fuzz-ep"] = conf["vm-part-off"]
    conf["vm-fuzz-ep-next"] = conf["vm-fuzz-ep"] + 4

# Ordered list of monitored memory areas
conf["vm-mem-ranges"] = "/tmp/pok_ranges.bin"

# for double quoted "keys" instead of default single quoted Dict
print json.dumps(conf)
