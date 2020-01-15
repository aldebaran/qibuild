#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display a complete description of a toolchain """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qitoolchain
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?", help="Name of the toolchain to print. Default: all")


def do(args):
    """ Main method """
    if args.name:
        tc_names = [args.name]
    else:
        tc_names = qitoolchain.get_tc_names()
    for tc_name in tc_names:
        toolchain = qitoolchain.get_toolchain(tc_name)
        ui.info(str(toolchain))
