## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)

def do(args):
    """Main entry point"""
    if args.work_tree:
        work_tree = args.work_tree
    else:
        work_tree = os.getcwd()
    qibuild.worktree.create(work_tree)

