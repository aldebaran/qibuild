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
    """ Add a package to a toolchain

    - Check that there is a current toolchain
    - Add the package to the cache
    - Add the package from cache to toolchain

    """
    package_name = args.package_name
    package_path = args.package_path
    tc = qitoolchain.get_toolchain(args)
    tc_cache_path = qitoolchain.get_tc_cache(tc.name)
    dest = os.path.join(tc_cache_path, package_name)
    in_cache = qibuild.archive.archive_name(dest)
    qibuild.sh.install(package_path, in_cache)
    tc.add_package(package_name, in_cache)
