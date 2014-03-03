#!/usr/bin/env python3

# decode.py: A program to decode Beddit sample data
# Copyright (c) 2014  Sami Liedes <sami.liedes@iki.fi>

# See the LICENSE file for license information.

import struct
import binascii
import sys

VERBOSE=False

class EOF(Exception):
    pass

class CRCError(Exception):
    def __init__(self, expected, computed):
        self.expected = expected
        self.computed = computed
    def __str__(self):
        return 'CRC error: expected 0x%08x, computed 0x%08x' % (
            self.expected, self.computed)

class InvalidPacket(Exception):
    def __str__(self):
        return 'Invalid packet'

def read_pkt(f):
    header = f.read(6)
    if len(header) != 6:
        raise EOF()
    pkt_num, pay_len = struct.unpack('<IH', header)
    if pay_len % 4 != 0:
        raise InvalidPacket()
    if pay_len > 65000:
        raise InvalidPacket()
    data = f.read(pay_len)
    if len(data) != pay_len:
        raise InvalidPacket() # also might be genuine EOF
    crc = f.read(4)
    if len(crc) != 4:
        raise InvalidPacket()
    crc = struct.unpack('<I', crc)[0]
    crc_calc = binascii.crc32(header+data) & 0xffffffff
    if crc != crc_calc:
        raise CRCError(crc, crc_calc)
    return pkt_num, data


def main():
    f = open('data.bin', 'rb')

    normal = []
    gained = []

    pkt_num = None
    resyncing = False
    while True:
        off = f.tell()
        old_pkt_num = pkt_num
        try:
            pkt_num, data = read_pkt(f)
            resyncing = False
        except EOF:
            break
        except (InvalidPacket, CRCError) as e:
            if not resyncing:
                print(str(e) + '; resyncing...')
                resyncing = True
            f.seek(off+1)
            continue

        if VERBOSE:
            print('%08x: Packet %d, length %d' % (off, pkt_num, len(data)))
        if old_pkt_num and pkt_num != old_pkt_num + 1:
            print('Warning: Inconsistent packet number at offset 0x%x: Expected %d, got %d.' % (
                off, old_pkt_num+1, pkt_num))

        samples = struct.unpack('<%dH' % (len(data)/2), data)
        normal += samples[0::2]
        gained += samples[1::2]

    f.close()

    with open('data.txt', 'w') as out:
        for n, g in zip(normal, gained):
            out.write('%d\t%d\n' % (n-32768, g-32768))


if __name__ == '__main__':
    main()
