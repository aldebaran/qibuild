## Copyright (C) 2011 Aldebaran Robotics

"""Init a new qisrc workspace """

import os
import qibuild
import qisrc


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)

def do(args):
    """Main entry point"""
    work_tree = qibuild.qiworktree.worktree_from_args(args)
    qibuild.qiworktree.create(work_tree)

