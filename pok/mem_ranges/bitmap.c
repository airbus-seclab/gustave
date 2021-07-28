//#include <gmodule.h>
#include <stdint.h>
#include <stdio.h>
#include <sys/mman.h>
#include <sys/stat.h>        /* For mode constants */
#include <fcntl.h>           /* For O_* constants */
#include <stdlib.h>
#include <unistd.h>
#include <signal.h>


typedef uint32_t target_ulong;

typedef uint32_t u32;
typedef uint64_t u64;

#define HASH_CONST     0xa5b35705
#define ROL64(_x, _r)  ((((u64)(_x)) << (_r)) | (((u64)(_x)) >> (64 - (_r))))

static inline u32 hash32(const void* key, u32 len, u32 seed) {

  const u64* data = (u64*)key;
  u64 h1 = seed ^ len;

  len >>= 3;

  while (len--) {

    u64 k1 = *data++;

    k1 *= 0x87c37b91114253d5ULL;
    k1  = ROL64(k1, 31);
    k1 *= 0x4cf5ad432745937fULL;

    h1 ^= k1;
    h1  = ROL64(h1, 27);
    h1  = h1 * 5 + 0x52dce729;

  }

  h1 ^= h1 >> 33;
  h1 *= 0xff51afd7ed558ccdULL;
  h1 ^= h1 >> 33;
  h1 *= 0xc4ceb9fe1a85ec53ULL;
  h1 ^= h1 >> 33;

  return h1;

}

//#include "range.h"

#define BITMAP_NAME "/GUSTAVE.BITMAP"
#define BITMAP_SIZE (1<<29)

static void test_addr(uint8_t *mm, target_ulong addr)
{
    unsigned int q = addr/8;
    unsigned int r = addr%8;
    printf("0x%x = %hhu | mq 0x%x q %u r %u\n",
	   addr, !!(mm[q] & (1<<r)),
	   mm[q],q,r);
}

static void test_all(uint8_t *mm, target_ulong *list, size_t nr)
{
    for (int i=0 ; i<nr ; i++) {
        test_addr(mm, list[i]);
    }
}

static void init_ranges(char *fname, void **rg, size_t *nr)
{
    struct stat st;
    if (stat(fname, &st) < 0) {
        perror("init_ranges: stat");
        exit(1);
    }

    int fd = open(fname, O_RDONLY);
    if (fd < 0) {
        perror("init_ranges: open");
        exit(1);
    }

    *rg = mmap(NULL, st.st_size, PROT_READ, MAP_PRIVATE, fd, 0);
    if (*rg == MAP_FAILED) {
        perror("init_ranges: mmap");
        exit(1);
    }

    *nr = st.st_size / (sizeof(target_ulong)*2);
}

#define DBG_RNG 0

static void init_ram_map(char *fname, uint8_t *mm)
{
    target_ulong (*ranges)[2] = NULL;
    size_t i,nr;

    init_ranges(fname, (void**)&ranges, &nr);

    for (i=0 ; i < nr ; i++) {

        target_ulong s = ranges[i][0];
        target_ulong e = ranges[i][1];

        target_ulong sq = s/8;
        target_ulong sr = s%8;

        target_ulong eq = e/8;
        target_ulong er = e%8;

        int debug = (s == DBG_RNG || e == DBG_RNG);

        if (debug) {
            fprintf(stderr,
		    "0x%x = sq %x sr %x eq %x er %x\n",
		    s, sq,sr,eq,er);
            fflush(stderr);
        }

        if (sq == eq) {
            while (sr <= er) { mm[sq] |= (1<<sr++); }
        } else {
            while (sr < 8)   { mm[sq] |= (1<<sr++); }
            sq++;
            while (sq < eq)  { mm[sq++] = 0xff; }
            sr = 0;
            while (sr <= er) { mm[sq] |= (1<<sr++); }
        }

        if (debug) {
            test_addr(mm, s);
            test_addr(mm, e);
        }
    }
}

void hdl_ctrl_c(int signum)
{
    printf("unlink shm\n");
    shm_unlink(BITMAP_NAME);
    exit(0);
}

int main(int argc, char **argv)
{
    uint8_t *mm;
    int      fd;

    fd = shm_open(BITMAP_NAME, O_RDONLY, S_IRUSR|S_IWUSR);
    if (fd < 0) {
        perror("shm_open(rdonly) ... try create");

	if (argc < 2) {
	    fprintf(stderr, "usage: %s <range file>\n", argv[0]);
	    exit(1);
	}

	fd = shm_open(BITMAP_NAME, O_RDWR|O_CREAT,
                      S_IRUSR|S_IWUSR);
        if (fd < 0) {
            perror("shm_open(create)");
            exit(1);
        }

        printf("create shm\n");

        if (ftruncate(fd, BITMAP_SIZE) < 0) {
            perror("ftruncate(shm)");
            exit(1);
        }

        mm = mmap(NULL, BITMAP_SIZE, PROT_READ|PROT_WRITE,
                  MAP_SHARED, fd, 0);

        if (mm == MAP_FAILED) {
            perror("mmap(create)");
            exit(1);
        }

        init_ram_map(argv[1], mm);
        printf("parsed bitmap\n");
	printf("hash32 0x%x\n",
	       hash32(mm, BITMAP_SIZE, HASH_CONST));

        signal(SIGINT, hdl_ctrl_c);
        char c;
        while(1) read(0,&c,1);

    } else { // existing file

        mm = mmap(NULL, BITMAP_SIZE, PROT_READ,
                  MAP_SHARED, fd, 0);
        if (mm == MAP_FAILED) {
            perror("mmap(read");
            exit(1);
        }
        printf("mmaped bitmap\n");
	printf("hash32 0x%x\n",
	       hash32(mm, BITMAP_SIZE, HASH_CONST));

        printf(" -- INCLUDED --\n");
        target_ulong included[] =
            {
             0xfff00100,
            };
        test_all(mm, included, sizeof(included)/sizeof(*included));

        printf(" -- EXCLUDED --\n");
        target_ulong excluded[] =
            {
             0xfffd0000,
            };
        test_all(mm, excluded, sizeof(excluded)/sizeof(*excluded));

        printf(" -- Enter address --\n");
        while(1) {
            char input[256];
            target_ulong addr =
                strtoul(fgets(input, sizeof(input), stdin), NULL, 16);
            test_addr(mm, addr);
        }
    }

    return 0;
}
