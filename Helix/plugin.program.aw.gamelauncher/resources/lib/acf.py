#!/usr/bin/env python3

# Copyright (c) 2012-2014 Ian Munsie <darkstarsword@gmail.com>
#               2014      Ingo Ruhnke <grumbel@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import sys
import argparse

# The acf files look like a pretty simple format - I wouldn't be surprised if a
# python parser already exists that can process it (even by chance), but I
# don't know of one offhand so here's a quick one I hacked up


def scan_for_next_token(f):
    while True:
        byte = f.read(1)
        if byte == '':
            raise EOFError
        if not byte.isspace():
            return byte


def parse_quoted_token(f):
    ret = ''
    while True:
        byte = f.read(1)
        if byte == '':
            raise EOFError
        if byte == '"':
            return ret
        ret += byte


class AcfNode(dict):

    def __init__(self, f):
        while True:
            try:
                token_type = scan_for_next_token(f)
            except EOFError:
                return
            if token_type == '}':
                return
            if token_type != '"':
                raise TypeError('Error parsing ACF format - missing node name?')
            name = parse_quoted_token(f)

            token_type = scan_for_next_token(f)
            if token_type == '"':
                self[name] = parse_quoted_token(f)
            elif token_type == '{':
                self[name] = AcfNode(f)
            else:
                assert(False)


def parse_acf(filename):
    with open(filename, 'r') as f:
        return AcfNode(f)


def main():
    parser = argparse.ArgumentParser(description='Steam acf parser')
    parser.add_argument('FILE', action='store', type=str, nargs='+',
                        help='file to process')
    parser.add_argument('--depots', action='store_true', default=False,
                        help='print depotcache info')
    args = parser.parse_args()

    if args.depots:
        for filename in args.FILE:
            acf = parse_acf(filename)
            installdir = acf['AppState']['installdir']
            depots = acf['AppState']['MountedDepots']
            for k, v in depots.items():
                print("%s_%s.manifest %s" % (k, v, installdir))
    else:
        for filename in args.FILE:
            acf = parse_acf(filename)
            print(acf)

if __name__ == '__main__':
    main()

# EOF #