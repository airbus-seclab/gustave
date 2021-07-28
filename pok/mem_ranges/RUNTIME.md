# POK firmware runtime memory organization (PPC)

## PPC in SRC mode

```
HEAP end |0xb4b10|
Partition 0 base=|16000| size=|9eb10|
pok_create_space: id 0 base 16000 sz 9eb10
HEAP end |0xb7000|
space_context_create 0: entry=80458 stack=9cb60 arg1=dead arg2=beaf ksp=b6fa0
HEAP end |0xd44c0|
Partition 1 base=|b7000| size=|1d4c0|
pok_create_space: id 1 base b7000 sz 1d4c0
HEAP end |0xd7000|
space_context_create 1: entry=454 stack=1b510 arg1=dead arg2=beaf ksp=d6fa0
HEAP end |0xd8000|
ctxt_create 5: sp=d7f98
POK kernel initialized
```

```
LOAD           0x010000 0xfff00000 0xfff00000 0xd7534 0xd7534 RWE 0x10000
LOAD           0x0f0000 0x00010000 0xfffd7534 0x00058 0x00058 RW  0x10000
LOAD           0x0f0060 0x00010060 0xfffd75a0 0x06624 0x06624 RW  0x10000
LOAD           0x0ffffc 0xfffffffc 0xfffffffc 0x00004 0x00004 R E 0x10000
```


## PPC in TCG mode

```
HEAP end |0xb4b10|
Partition 0 base=|16000| size=|9eb10|
pok_create_space: id 0 base 16000 sz 9eb10
HEAP end |0xb7000|
space_context_create 0: entry=80458 stack=9cb60 arg1=dead arg2=beaf ksp=b6fa0
HEAP end |0xd44c0|
Partition 1 base=|b7000| size=|1d4c0|
pok_create_space: id 1 base b7000 sz 1d4c0
HEAP end |0xd7000|
space_context_create 1: entry=454 stack=1b510 arg1=dead arg2=beaf ksp=d6fa0
HEAP end |0xd8000|
ctxt_create 5: sp=d7f98
POK kernel initialized
```

```
LOAD  0x010000 0xfff00000 0xfff00000 0xb5830 0xb5830 RWE 0x10000
LOAD  0x0d0000 0x00010000 0xfffb5830 0x06444 0x06444 RW  0x10000
LOAD  0x0dfffc 0xfffffffc 0xfffffffc 0x00004 0x00004 R E 0x10000
```
