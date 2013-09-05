#!/usr/bin/env python

## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" To be used from ``qicd`` shell function

"""

import os
import sys

if __name__ == '__main__':
    try:
        major = sys.version_info.major
    except AttributeError:
        # Python < 2.7
        major = sys.version_info[0]
    if major != 2:
        res = 1
        try:
            import subprocess
            res = subprocess.call(['python2'] + sys.argv)
        except OSError as e:
            print(e)
        sys.exit(res)

# sys.path
def patch_sys_path():
    """
    Add self sources to sys.path, so that directly using this script
    from the sources works

    """
    this_dir = os.path.dirname(__file__)
    to_add =  os.path.join(this_dir, "..")
    to_add = os.path.abspath(to_add)
    sys.path.insert(0, to_add)


patch_sys_path()

import qisys.worktree
import qisys.parsers

