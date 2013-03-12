## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Initialize a new toc worktree """

import os
import sys

from qisys import ui
import qisys.worktree
import qibuild.worktree


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)

def do(args):
    """Main entry point"""
    root = os.getcwd()
    if not qisys.sh.is_empty(root):
        raise Exception("Please run this command from an empty directory")
    worktree = qisys.worktree.WorkTree(root)
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
