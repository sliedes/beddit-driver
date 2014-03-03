#!/usr/bin/env python3

# measure.py: A program to communicate with a Beddit sensor
# Copyright (c) 2014  Sami Liedes <sami.liedes@iki.fi>

# See the LICENSE file for license information.

import sys
import os
import fcntl
import select
import time
import binascii

def set_nonblock(f):
    fd = f.fileno()
    flags = fcntl.fcntl(f, fcntl.F_GETFL)
    fcntl.fcntl(f, fcntl.F_SETFL, flags | os.O_NONBLOCK)

def assert_not_exists(fname):
    try:
        open(fname)
        print("Error: move %s out of the way." % fname, file=sys.stderr)
        sys.exit(1)
    except IOError:
        pass

def p(dev, s):
    return dev.write(bytes(s, 'ascii'))

def wait_write(dev):
    return select.select([], [dev], [dev])

def main():
    assert_not_exists('data.out')

    data_out = open('data.out', 'w')

    dev = open(sys.argv[1], 'rb+', 0)
    print("Opened device %s." % sys.argv[1])
    print("> OK")
    wait_write(dev)
    p(dev, 'OK\n')
    print("Reading response.")
    l = dev.readline()
    print("< " + l.decode('ascii').rstrip())
    print("> INFO")
    p(dev, 'INFO\n')
    l = dev.readline()
    print("< " + l.decode('ascii').rstrip())
    set_nonblock(dev)
    print("> START")
    p(dev, "START\n")

    start_t = time.time()
    while True:
        select.select([dev], [], [dev])
        t = time.time()-start_t
        data = dev.read()
        print('%.6f\t%d\t%s' % (t, len(data),
                                binascii.hexlify(data).decode('ascii')),
              file=data_out)
        if not data:
              break


if __name__ == '__main__':
    main()
