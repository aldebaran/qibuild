## Copyright (C) 2011 Aldebaran Robotics

""" Configure a worktree to use a toolchain.

Toolchain packages and known configurations will be fetched from an URL.

"""

import sys
import logging

import qibuild

LOGGER = logging.getLogger(__name__)



def configure_parser(parser):
    """Configure parse for this action """
    qibuild.worktree.work_tree_parser(parser)


def do(args):
    """Main entry point

    """
    pass
