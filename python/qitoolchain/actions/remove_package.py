#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Remove a package from a toolchain """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qitoolchain.parsers
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qitoolchain.parsers.toolchain_parser(parser)
    parser.add_argument("package_name", metavar='NAME',
                        help="The name of the package to remove")


def do(args):
    """
    Remove a project from a toolchain
    - Check that there is a current toolchain
    - Remove the package from the toolchain
    """
    package_name = args.package_name
    toolchain = qitoolchain.parsers.get_toolchain(args)
    ui.info(ui.green, "Removing package", ui.blue, package_name,
            ui.green, "from toolchain", ui.blue, toolchain.name)
    toolchain.remove_package(package_name)
