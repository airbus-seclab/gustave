#!/bin/bash

if [ $# -ne 2 ] ; then
    echo -ne "\nusage: $0 <src|tcg> <i386|kvm|ppc>\n\n"
    echo -ne "  'src', kernel source code coverage with AFL shims\n"
    echo -ne "  'tcg', QEMU binary instrumentation coverage\n"
    echo -ne "\n! 'kvm' is not available when 'tcg' is selected !\n\n"
    exit 1
fi

ROOT=$(git rev-parse --show-toplevel)/pok
CONFIG="${ROOT}/.gustave.env"
> $CONFIG

add_cfg () {
    echo "$1" >> $CONFIG
}

# parse args
arg_mode=$1
arg_arch=$2

QBLD=""
QOPT=""
if [ $arg_arch == kvm ];then
    QEMU_ARCH=x86_64
    QBLD="--enable-kvm"
    QOPT="-accel kvm --cpu host"
else
    QEMU_ARCH=$arg_arch
fi

QFLG="-DAFL_TARGET_POK"
if [ $arg_mode == src ];then
    AFL_POK_COV=src
elif [ $arg_mode == tcg ];then
    if [ $arg_arch == kvm ];then
        echo "unsupported arch for mode !"
        exit 1
    fi
    QFLG+=" -DAFL_TCG"
    AFL_POK_COV=tcg
else
    echo "invalide mode: $arg_mode"
    exit 1
fi

GDB_PATH="\${ROOT}/gdb"
AFL_PATH="\${ROOT}/afl-git"
POK_PATH="\${ROOT}/pok-git"
QEMU_PATH="\${ROOT}/qemu-git"
QEMU_BUILD="\${QEMU_PATH}/build"

AFL_BUILD=""
if [ $QEMU_ARCH == i386 ] || [ $QEMU_ARCH == x86_64 ] ; then
    POK_ARCH=x86
    GDB=gdb
    QOPT="-M afl -nographic ${QOPT} -kernel \${POK_VM}/pok.elf"
    QBLD="--target-list=${QEMU_ARCH}-softmmu --disable-user --disable-sdl --disable-tpm --disable-libxml2 --disable-cap-ng --disable-curses --disable-vnc --disable-blobs --disable-guest-agent"

elif [ $QEMU_ARCH == ppc ] ; then
    if [ $AFL_POK_COV == src ];then
        AFL_BUILD="AFL_NO_X86=1"
    fi
    POK_ARCH=ppc
    GDB=gdb-multiarch
    QOPT="-M afl -nographic -bios \${POK_VM}/rom.bin"
    QBLD="--target-list=ppc-softmmu --disable-user --disable-sdl --disable-tpm --disable-libxml2 --disable-cap-ng --disable-curses --disable-vnc --disable-blobs --disable-kvm --disable-guest-agent"

else
    echo "invalid architecture: $QEMU_ARCH"
    exit 1
fi

POK_VM="\${POK_PATH}/examples/gustave_${POK_ARCH}"
GDB_SCRIPT="\${GDB_PATH}/gdbrc_${POK_ARCH}"
QJSON="\${ROOT}/config/pok_${POK_ARCH}_${AFL_POK_COV}.json"
QCONF="-gustave \${QJSON}"
QBIN="\${QEMU_BUILD}/qemu-system-${QEMU_ARCH}"
QOPT="${QOPT} \${QCONF}"
QRUN="\${QBIN} \${QOPT}"


## AFL
AFL_IN=/tmp/afl_in
AFL_OUT=/tmp/afl_out
AFL_TIMEOUT=3000+
AFL_OPTS="-m none -t \${AFL_TIMEOUT} -i \${AFL_IN} -o \${AFL_OUT}"
AFL_BIN="\${AFL_PATH}/afl-fuzz"
AFL="\${AFL_BIN} \${AFL_OPTS}"


# Commit variables
add_cfg "export GDB_PATH=$GDB_PATH"
add_cfg "export POK_PATH=$POK_PATH"
add_cfg "export POK_VM=$POK_VM"
add_cfg "export POK_ARCH=$POK_ARCH"
add_cfg "export QEMU_ARCH=$QEMU_ARCH"
add_cfg "export QEMU_PATH=$QEMU_PATH"
add_cfg "export QEMU_BUILD=$QEMU_BUILD"
add_cfg "export AFL_FAST_CAL=1"
add_cfg "export AFL_SKIP_BIN_CHECK=1"
add_cfg "export AFL_PATH=$AFL_PATH"
add_cfg "export AFL_POK_COV=$AFL_POK_COV"
[ ! -z $AFL_BUILD ] && add_cfg "export $AFL_BUILD"

add_cfg "GDB=$GDB"
add_cfg "GDB_SCRIPT=$GDB_SCRIPT"
add_cfg "QBIN=$QBIN"
add_cfg "QBLD=\"$QBLD\""
add_cfg "QFLG=\"$QFLG\""
add_cfg "QJSON=$QJSON"
add_cfg "QCONF=\"$QCONF\""
add_cfg "QOPT=\"$QOPT\""
add_cfg "QRUN=\"$QRUN\""

add_cfg "AFL_IN=$AFL_IN"
add_cfg "AFL_OUT=$AFL_OUT"
add_cfg "AFL_TIMEOUT=$AFL_TIMEOUT"
add_cfg "AFL_OPTS=\"$AFL_OPTS\""
add_cfg "AFL_BIN=$AFL_BIN"
add_cfg "AFL=\"$AFL\""

echo -e "\n\t---- GUSTAVE environment ----\n"
cat $CONFIG
echo
