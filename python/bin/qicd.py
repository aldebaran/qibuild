#!/usr/bin/env python

## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" To be used from a shell function
"""

import re
import os
import sys

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

import qisrc

def main():
    try:
        worktree = qisrc.worktree.open_worktree()
    except Exception:
        sys.stderr.write("Not in a worktree")
        sys.exit(2)
    if len(sys.argv) < 2:
        sys.stdout.write(worktree.root + "\n")
        sys.exit(0)
    token = sys.argv[1]
    for project in worktree.projects:
        match = re.search("^(.*?/)?%s" % token, project.src)
        if match:
            sys.stdout.write(project.path + "\n")
            sys.exit(0)
    # no match
    sys.stderr.write("no match for %s\n" % token)
    sys.stdout.write(worktree.root + "\n")
    sys.exit(0)


if __name__ == "__main__":
    main()

