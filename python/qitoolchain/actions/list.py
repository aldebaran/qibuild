#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display the toolchains names. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qitoolchain
import qisys.parsers
import qisys.worktree
from qisys import ui


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    if not tc_names:
        ui.info("No toolchain yet", "\n",
                "Use `qitoolchain create` to create a new toolchain")
        return
    ui.info("Known toolchains:")
    for tc_name in tc_names:
        ui.info("*", tc_name)
    ui.info("Use ``qitoolchain info <tc_name>`` for more info")
