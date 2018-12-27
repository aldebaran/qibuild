#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Remove a complete virtualenv """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qipy.parsers
import qipy.worktree
import qibuild.parsers
import qisys.sh
import qisys.command
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("-f", "--force", dest="force", action="store_true")


def do(args):
    """ Main Entry Point """
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    venv_path = python_worktree.venv_path
    if not args.force:
        ui.info("Would delete", venv_path)
    else:
        ui.info("Removing", venv_path)
        qisys.sh.rm(venv_path)
