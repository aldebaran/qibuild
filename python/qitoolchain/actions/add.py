## Copyright (C) 2011 Aldebaran Robotics

"""Add a new package to a toolchain
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
        help="The name of the package")
    parser.add_argument("package_path", metavar='PATH',
        help="The path to the package")

def do(args):
    """ Add a project to a toolchain

    - Check that there is a current toolchain
    - Run `qibuild package' if a project, and not a package was given as
        argument
    - Add the package to the cache
    - Add the package from cache to toolchain

    """
    package_name = args.package_name
    package_path = args.package_path
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
            mess  = "(not in a work tree or not default config in "
            mess += "current worktree configuration)\n"
            mess += "Please specify a configuration with -c \n"
            raise Exception(mess)
        tc_name = active_config

    tc_cache_path = qitoolchain.get_tc_cache(tc_name)
    dest = os.path.join(tc_cache_path, package_name)
    in_cache = qibuild.archive.archive_name(dest)

    qibuild.sh.install(package_path, in_cache)

    tc = qitoolchain.Toolchain(tc_name)
    tc.add_package(package_name, in_cache)
