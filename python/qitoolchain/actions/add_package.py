## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
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
    parser.add_argument("package_path", metavar='PATH',
                        help="The path to the package")

def do(args):
    """ Add a package to a toolchain

    - Check that there is a current toolchain
    - Add the package to the cache
    - Add the package from cache to toolchain

    """
    toolchain = qitoolchain.parsers.get_toolchain(args)
    package_path = args.package_path
    package = qitoolchain.qipackage.from_archive(package_path)

    # extract it to the default packages path of the toolchain
    tc_name = toolchain.name
    tc_packages_path = qitoolchain.toolchain.get_default_packages_path(tc_name)
    dest = os.path.join(tc_packages_path, package.name)
    qisys.sh.rm(dest)
    qisys.archive.extract(package_path, dest, strict_mode=False)
    package.path = dest

    # add the package to the toolchain
    toolchain.add_package(package)
