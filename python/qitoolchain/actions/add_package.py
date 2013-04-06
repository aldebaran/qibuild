## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Add a new package to a toolchain

"""

import os

import qisys.archive
import qisys.worktree
import qitoolchain.parsers

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-c", "--config",
                        help="name of the toolchain to use")
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
    toolchain = qitoolchain.parsers.get_toolchain(args)
    package_name = args.package_name
    package_path = args.package_path
    # extract it to the default packages path of the toolchain
    tc_name = toolchain.name
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc_name)
    dest = os.path.join(tc_packages_path, package_name)
    qisys.sh.rm(dest)
    with qisys.sh.TempDir() as tmp:
        extracted = qisys.archive.extract(package_path, tmp)
        qisys.sh.install(extracted, dest, quiet=True)

    package = qitoolchain.Package(package_name, dest)
    toolchain.add_package(package)
