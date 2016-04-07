#!/usr/bin/env python
# coding: utf-8

''' Transfer files to another place using SCP.

Usage:
    ./transfer_files [options]

Options:
    -h --help                                 Show this message.
    -i --instance <instance_folder_path>      Instance folder path.
    -s --store-folder <store_folder_path>     Folder where to store downloaded.
    -p --public-folder <public_folder_path>   Folder where to store files to be
'''

from __future__ import unicode_literals  # unicode by default
import os

import pexpect
from docopt import docopt


if __name__ == '__main__':
    arguments = docopt(__doc__)

    instance_path = arguments['--instance']
    public_downloads = arguments['--public-folder']
    storing_folder = arguments['--store-folder']

    place, password = (open(os.path.join(instance_path, 'transfer.conf'), 'r')
                       .read().strip().split())

    def transfer(from_, to_):
        c = 'scp -o "StrictHostKeyChecking no" %s %s:%s' % (from_, place, to_)
        processo = pexpect.spawn(c)
        processo.expect('password: ')
        processo.sendline(password)
        processo.expect(pexpect.EOF)

    files = os.listdir(public_downloads)
    for f in files:
        file_ = os.path.join(public_downloads, f)
        transfer(file_, '~/public/')
        os.remove(file_)

    files = os.listdir(storing_folder)
    for f in files:
        if not f.startswith('last'):
            file_ = os.path.join(storing_folder, f)
            transfer(file_, '~/public/diarios')
            os.remove(file_)
