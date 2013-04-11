## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Add a new package to a toolchain

"""

import os

import qisys
import qisys.archive
import qisys.worktree
import qibuild
import qibuild.toc
import qibuild.parsers
import qitoolchain

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
    tc_name = qitoolchain.toolchain_name_from_args(args)
    tc = qitoolchain.get_toolchain(tc_name)
    # extract it to the default packages path of the toolchain
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc.name)
    dest = os.path.join(tc_packages_path, package_name)
    qisys.sh.rm(dest)
    with qisys.sh.TempDir() as tmp:
        extracted = qisys.archive.extract(package_path, tmp)
        qisys.sh.install(extracted, dest, quiet=True)

    package = qitoolchain.Package(package_name, dest)
    tc.add_package(package)
