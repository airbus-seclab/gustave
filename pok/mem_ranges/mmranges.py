#!/usr/bin/env python
#
# cf. README.md for details on POK memory 
#

#from __future__ import print_function
import sys, struct

if len(sys.argv) < 2:
    print("need file name")
    sys.exit(1)

def covers(r1,r2):
    return not (r1[1] < r2[0] or r1[0] > r2[1])

def contiguous(r1,r2):
    return (r1[1] == (r2[0] -1) or  r2[1] == (r1[0] -1))
    
def fusion(r1,r2):
    return [min(r1[0],r2[0]), max(r1[1],r2[1])]

def merge(n,rg):
    global ranges
    for i in range(n,len(ranges)):
        r = ranges[i]
        if covers(r,rg) or contiguous(r,rg):
            ranges[i] = fusion(r,rg)
            return i

    ranges.append(rg)
    return len(ranges)-1


fname = sys.argv[1]
ranges = [ [0,0] ]
n = 0
data = open(fname).readlines()

print("NFO: building ranges...")
total=len(data)
progress=0
fprogress=0
for l in data:
    if l.startswith("#") or len(l) == 1 : # comments, empty
        continue
    try:
        st,sa,ss = l.split() # tag start size
    except:
        print("Error with: %s" % (l))
        sys.exit(1)

    addr = int(sa,16)
    if ss.startswith("0x"):
        base=16
    else:
        base=10
    sz = int(ss,base)

    # inclusive range
    start = addr
    end   = start+sz-1
    rg = [start, end]

    n = merge(n, rg)

    progress += 1
    fprogress += 1
    if (progress*100)/total >= 5:
        progress = 0
        rate = (fprogress*100)/total
        fmt = "progress = %f (%d/%d)\r" % (rate, fprogress, total)
        print fmt,
        sys.stdout.flush()
        # d1,d2=ranges[0][0],ranges[0][1]
        # d3,d4=ranges[-1][0], ranges[-1][1]
        # print("#ranges %d : (0x%08x - 0x%08x) | (0x%08x - 0x%08x)" % \
        #     (len(ranges), d1,d2,d3,d4))


###
### Byte ranges
###
print("---- byte ranges (%d) ----" % (len(ranges)))

####
#### Page ranges
####
PAGE_RANGE_enable=False

if PAGE_RANGE_enable:
    pranges = [ [ranges[0][0]&(~0xfff),ranges[0][1]&(~0xfff)] ]
    n=0
    for i,r in enumerate(ranges[1:]):
        rs = r[0] & (~0xfff)
        os = r[0] & 0xfff
        re = r[1] & (~0xfff)
        oe = r[1] & 0xfff
        #print("  r %x %x" % (rs,re))

        xe = pranges[n][1] & (~0xfff)
        if xe == (rs - 0x1000):
            xe = re + oe
            #print("fusion: %x %x" % (pranges[n][0],pranges[n][1]))
        elif rs > xe:
            #print("crt: %x %x" % (pranges[n][0],pranges[n][1]))
            #print("add: %x %x" % (rs,re))
            #if rs == 0xfff00000:
            #   print("add: %x %x" % (rs,re))
            pranges.append([rs+os,re+oe])
            #pranges.append([rs,re])
            n +=1

    print("---- page ranges (%d) ----" % (len(pranges)))
    active_ranges = pranges
else:
    active_ranges = ranges
    
###
### Bitmap range
###
bitmap  = ""
srange  = ""
for r in active_ranges:
    s = r[0]
    e = r[1]
    srange += "0x%08x - 0x%08x\n" % (s,e)
    bitmap += struct.pack("<LL", s,e)

open(fname+".ranges", "w").write(srange)
open(fname+".bitmap", "w").write(bitmap)
