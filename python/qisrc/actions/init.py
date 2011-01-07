##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##
## Copyright (C) 2010, 2011 Aldebaran Robotics
##

"""Init a new qisrc workspace """

import os
import qitools
import qisrc


def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)

def do(args):
    """Main entry point"""
    work_tree = qitools.qiworktree.worktree_from_args(args)
    qitools.qiworktree.create(work_tree)

