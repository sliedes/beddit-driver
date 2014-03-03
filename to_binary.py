#!/usr/bin/env python3

# A small tool to convert timestamped hex capture of data to a
# non-timestamped binary format.

# See the LICENSE file for license information.

import binascii

f = open('data.out', 'r')
out = open('data.bin', 'wb')

for line in f:
    ts,nbytes,data = line.strip().split('\t')
    d = binascii.unhexlify(data)
    out.write(d)
