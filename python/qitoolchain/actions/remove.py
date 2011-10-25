## Copyright (C) 2011 Aldebaran Robotics

"""Uninstall a toolchain

"""

import logging

import qibuild
import qitoolchain

import ConfigParser

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.worktree.work_tree_parser(parser)
    parser.add_argument("name",
        help="The name of the toolchain to remove")

def do(args):
    """ Main entry point  """
    tc_name = args.name
    toolchain = qitoolchain.Toolchain(tc_name)
    LOGGER.info("Removing toolchain %s", tc_name)
    toolchain.remove()
    LOGGER.info("Done removing toolchain %s", tc_name)
