#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display info about a toolchain package """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qitoolchain.parsers
import qisys.parsers
from qisys import ui


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
