#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>        /* For mode constants */
#include <fcntl.h>           /* For O_* constants */
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>

#define BITMAP_NAME "/GUSTAVE.BITMAP"
void main(void) { printf("unlink_shm = %d\n", shm_unlink(BITMAP_NAME)); }
