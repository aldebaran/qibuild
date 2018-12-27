#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Uninstall a toolchain """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qitoolchain
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name",
                        help="The name of the toolchain to remove")
    parser.add_argument('-i', "--ignore",
                        dest="ignore", action="store_false",
                        help="""Ignore error if the toolchain does not exists.""")
    parser.add_argument('-f', "--force",
                        dest="force", action="store_true",
                        help="""remove the whole toolchain, including any local packages you may
             have added to the toolchain.""")


def do(args):
    """ Main entry point  """
    tc = qitoolchain.get_toolchain(args.name, args.ignore)
    if tc:
        if args.force:
            ui.info(ui.green, "Removing toolchain", ui.blue, tc.name)
            tc.remove()
            ui.info(ui.green, "done")
        else:
            ui.info("Would remove toolchain", ui.blue, tc.name)
            ui.info("Use --force to actually remove it.")
            return
    else:
        ui.info("Would remove toolchain", ui.blue, args.name)
        ui.info("This toolchain does not exists.")
        return
