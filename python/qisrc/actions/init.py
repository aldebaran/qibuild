## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)

def do(args):
    """Main entry point"""
    if args.worktree:
        worktree = args.worktree
    else:
        worktree = os.getcwd()
    qibuild.worktree.create(worktree)

