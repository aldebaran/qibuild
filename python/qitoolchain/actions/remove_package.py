## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Remove a package from a toolchain

"""

from qisys import ui
import qisys.parsers
import qitoolchain.parsers

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qitoolchain.parsers.toolchain_parser(parser)
    parser.add_argument("package_name", metavar='NAME',
                        help="The name of the package to remove")

def do(args):
    """ Remove a project from a toolchain

    - Check that there is a current toolchain
    - Remove the package from the toolchain

    """
    package_name = args.package_name
    toolchain = qitoolchain.parsers.get_toolchain(args)
    ui.info(ui.green, "Removing package", ui.blue, package_name,
            ui.green, "from toolchain", ui.blue, toolchain.name)
    toolchain.remove_package(package_name)
