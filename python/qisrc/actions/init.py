## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)

def do(args):
    """Main entry point"""
    work_tree = qibuild.worktree.worktree_from_args(args)
    qibuild.worktree.create(work_tree)

