#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Collect all python test in worktree """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.parsers
import qipy.parsers
from qisys import ui
from qitest.collector import PythonTestCollector


def configure_parser(parser):
    """ Configure Parser """
    qibuild.parsers.cmake_build_parser(parser)


def do(args):
    """ Main Entry Point """
    python_worktree = qipy.parsers.get_python_worktree(args)
    ui.info(ui.green, "python projects in:", ui.blue, python_worktree.root)
    collector = PythonTestCollector(python_worktree)
    collector.collect()
