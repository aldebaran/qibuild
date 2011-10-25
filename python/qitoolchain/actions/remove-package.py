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
    tc = qitoolchain.get_toolchain(args)

    LOGGER.info("Removing package %s from toolchain %s", package_name, tc.name)
    tc.remove_package(package_name)
