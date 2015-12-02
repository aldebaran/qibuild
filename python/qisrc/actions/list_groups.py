## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" List the available groups

"""

from qisys import ui
import qisrc.parsers
import qisys.qixml

import sys
import os

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)


def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    local_groups = git_worktree._syncer.manifest.groups

    all_groups= list()
    groups_elem = qisrc.groups.get_root(git_worktree)
    if groups_elem is None:
        groups_elem = list()
    for group_elem in groups_elem:
        all_groups.append(group_elem.get("name"))

    all_groups.sort()
    for group in all_groups:
        if group in local_groups:
            ui.info("*", ui.green, group)
        else:
            ui.info(" ", group)
