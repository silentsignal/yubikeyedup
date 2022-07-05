#!/usr/bin/env python3

'''
Write a new AES key to a YubiKey, and store it into a sqlite3 database.
'''

import distutils.spawn
import os
import sys
import subprocess


def hex2modhex(string):
    l = [ ('0123456789abcdef'[i], 'cbdefghijklnrtuv'[i]) for i in range(16) ]
    modhex = ''.join(dict(l).get(chr(j), '?') for j in range(256))
    return string.translate(modhex)

def get_public(name):
    return name.rjust(8, 'q')[:8]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s <name> <db.sqlite3>' % sys.argv[0])
        print('eg: %s bobama db/yubikeys.sqlite3' % sys.argv[0])
        sys.exit(0)

    name = sys.argv[1]
    db = sys.argv[2]
    aeskey = os.urandom(16).hex()
    public = get_public(name).encode('utf-8').hex()
    public_m = hex2modhex(public)
    uid = os.urandom(6).hex()

    cmd = [ 'ykman', 'otp', 'yubiotp',
            '1',
            '-P', public_m,
            '-p', uid,
            '-k', aeskey
    ]

    print(cmd)

    try:
        ret = subprocess.call(cmd)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print('%s: command not found.' % cmd[0])
            sys.exit(1)
        else:
            raise

    cwd = os.path.dirname(os.path.realpath(__file__))
    dbconf = os.path.join(cwd, 'dbconf.py')
    subprocess.call([ dbconf, '-yk', name, db ])
    subprocess.call([ dbconf, '-ya', name, public_m, uid, aeskey, db ])
    subprocess.call([ dbconf, '-yl', db])
