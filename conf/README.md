# Configuration file for GUSTAVE target

Our QEMU-AFL board takes a `-gustave <file.json>` option to provide
QEMU with target configuration.

The JSON file follows strict basic RFC format. No comment, no hexa.

It's parsed by `qemu/qom/qjson` parser and mapped to our board config
struct.

The structure is detailed below (see
[afl.h](https://github.com/airbus-seclab/qemu/blob/gustave/include/qemu/afl.h#L236))

```c
   struct __afl_qemu_conf {
      int64_t     timeout;  /* AFL cmd line user time out in ms */
      int64_t     overhead; /* Estimated overhead for qemu/afl
                             * transitions used to setup timer */
      const char *vms_tpl;  /* vmstate template file path */
   } qemu;

   /* AFL internals */
   struct __afl_int_conf {
      int         ctl_fd;     /* AFL control file descriptor */
      int         sts_fd;     /* AFL status file descriptor */
      size_t      trace_size; /* AFL coverage bitmap size in bytes */
      uint64_t    trace_addr; /* AFL coverage bitmap target mmio
                               * address */
      const char *trace_env;  /* AFL coverage bitmap shared memory
                               * identifier environment variable
                               * name */
   } afl;

   /* Virtual Machine (Target) partition information */
   struct __afl_target_conf {
      target_ulong  part_base;        /* Partition base paddr */
      uint64_t      part_size;        /* Allocated partition size */
      target_ulong  part_kstack;      /* Partition thread allocated
                                       * kernel stack vaddr */
      uint64_t      part_kstack_size; /* Partition thread allocated
                                       * kernel stack size */
      uint64_t      nop_size;         /* NOP-sled size */
      target_ulong  part_off;         /* NOP-sled offset */
      target_ulong  fuzz_inj;         /* Generated code injection paddr */
      target_ulong  fuzz_ep;          /* Fuzzing starting point vaddr */
      target_ulong  fuzz_ep_next;     /* Insn vaddr following FUZZ_EP */
      target_ulong  size;             /* Effective target physical memory
                                       * used */
      target_ulong  panic;            /* Target 'kernel panic' vaddr */
      target_ulong  cswitch;          /* Target context switch vaddr */
      target_ulong  cswitch_next;     /* Insn vaddr follwing 'vm_cswitch_next' */
   } tgt;
```
