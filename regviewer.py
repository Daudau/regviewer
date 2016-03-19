#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
import os
import re
import core.explorer as explorer
from optparse import OptionParser

# Tool version
VERSION = '0.1'

def main(argv=None):
    parser = OptionParser()
    parser.add_option("-y", "--system-hive", dest="system_hive", default=None,
                    help="Specify the absolute path to the system hive")
    parser.add_option("-o", "--software-hive", dest="software_hive",
                    default=None,
                    help="Specify the absolute path to the software hive")
    parser.add_option("-a", "--sam-hive", dest="sam_hive", default=None,
                    help="Specify the absolute path to the sam hive")
    parser.add_option("-u", "--users-hives", dest="users_hives", default=None,
                    help="Specify a list of (username, user_hive) couples")
    (options, args) = parser.parse_args()

    users_hives = None
    if options.users_hives:
        pattern = re.compile("^\[(\([a-zA-Z0-9.\s-]+,[a-zA-Z0-9./\s-]+\)(\s*,\s*)?)+\]$")
        if not pattern.match(options.users_hives):
            print("Wrong pattern for given users hives.")
            sys.exit(-1)
        users_hives = []
        for couples in options.users_hives.split("(")[1::]:
            couple = couples.split(")")[0].split(",")
            users_hives += [(couple[0], couple[1])]

    explorer.explore(options.system_hive, options.software_hive, options.sam_hive,
        users_hives)


if __name__ == '__main__':
    main()

