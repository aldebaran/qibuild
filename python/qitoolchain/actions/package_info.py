# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Display info about a toolchain package """

from qisys import ui
import qisys.parsers
import qitoolchain.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qitoolchain.parsers.toolchain_parser(parser)
    parser.add_argument("package_name")


def do(args):
    """ Main entry point """
    toolchain = qitoolchain.parsers.get_toolchain(args)
    package = toolchain.get_package(args.package_name, raises=True)
    package.load_package_xml()
    ui.info(package.name, package.version)
    ui.info("path:", package.path)
    if package.license:
        ui.info("license:", package.license)
