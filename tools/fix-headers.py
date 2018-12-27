#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

HEADER = """## Copyright (C) 2011-2019 SoftBank Robotics\n"""


def fix_file(filename):
    """ Fix File """
    start_header = -1
    end_header = -1
    was_in_header = False
    seen_header = False
    seen_shebang = False
    with open(filename, "r") as fp:
        lines = fp.readlines()
    for (i, line) in enumerate(lines):
        if line.startswith("#!"):
            seen_shebang = True
            continue
        if line.startswith("#"):
            if not seen_header:
                start_header = i
                was_in_header = True
                seen_header = True
                continue
        else:
            if was_in_header:
                end_header = i
                was_in_header = False
                continue
    header_lines = [l + "\n" for l in HEADER.splitlines()]
    if not seen_header:
        if seen_shebang:
            new_lines = [lines[0]] + header_lines + lines[1:]
        else:
            new_lines = header_lines + lines
    else:
        new_lines = lines[:start_header] +\
            header_lines +\
            lines[end_header:]
    with open(filename, "w") as fp:
        fp.writelines(new_lines)


if __name__ == "__main__":
    for filearg in sys.argv[1:]:
        print("fixing ", filearg)
        fix_file(filearg)
