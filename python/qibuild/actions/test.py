#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Launch automatic tests -- deprecated, use `qitest run` instead. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.parsers
import qitest.parsers
import qitest.actions.run
import qisys.script
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qitest.parsers.test_parser(parser)
    qibuild.parsers.project_parser(parser)
    qisys.parsers.build_parser(parser, include_worktree_parser=False)
    parser.add_argument("-l", "--list", dest="list", action="store_true",
                        help="List what tests would be run")


def do(args):
    """ Main entry point. """
    if args.list:
        ui.warning("`qibuild test --list` is deprecated, use `qitest list` instead")
        qisys.script.run_action("qitest.actions.list", forward_args=args)
    else:
        projects = args.projects
        ui.warning("`qibuild test` is deprecated, use `qitest run` instead")
        qisys.script.run_action("qitest.actions.run", args=projects,
                                forward_args=args)
