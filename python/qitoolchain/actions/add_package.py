## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

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
    # extract it to the default packages path of the toolchain
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc.name)
    dest = os.path.join(tc_packages_path, package_name)
    qibuild.sh.rm(dest)
    with qibuild.sh.TempDir() as tmp:
        extracted = qibuild.archive.extract(package_path, tmp)
        qibuild.sh.install(extracted, dest, quiet=True)

    package = qitoolchain.Package(package_name, dest)
    tc.add_package(package)
