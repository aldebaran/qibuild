## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Remove a group from the current worktree

"""

from qisys import ui
import qisrc.parsers

import sys
import copy

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("group")


def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    group = args.group
    manifest = git_worktree.manifest
    groups = copy.copy(git_worktree.manifest.groups)
    if group in groups:
        groups.remove(args.group)
    else:
        ui.info("No such group:", group)
        sys.exit(0)
    git_worktree.configure_manifest(manifest.url, groups=groups,
                                    branch=manifest.branch)
