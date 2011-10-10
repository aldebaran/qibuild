## Copyright (C) 2011 Aldebaran Robotics

"""Remove a package from a toolchain
"""

import os
import logging

import qibuild
import qitoolchain

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("package_name", metavar='NAME',
        help="The name of the package to remove")

def do(args):
    """ Remove a project from a toolchain

    - Check that there is a current toolchain
    - Remove the package from the toolchain

    """
    package_name = args.package_name
    tc_name = args.config

    if not tc_name:
        active_config = None
        try:
            toc = qibuild.toc.toc_open(args.work_tree, args)
            active_config = toc.active_config
        except qibuild.toc.TocException:
            pass
        if not active_config:
            mess  = "Could not find which config to use.\n"
            mess  = "(not in a work tree or no default config in "
            mess += "current worktree configuration)\n"
            mess += "Please specify a configuration with -c \n"
            raise Exception(mess)
        tc_name = active_config


    LOGGER.info("Removing package %s from toolchain %s", package_name, tc_name)
    tc_cache_path = qitoolchain.get_tc_cache(tc_name)
    in_cache = os.path.join(tc_cache_path, package_name)
    in_cache = qibuild.archive.archive_name(in_cache)

    qibuild.sh.rm(in_cache)

    tc = qitoolchain.Toolchain(tc_name)
    tc.remove_package(package_name)
