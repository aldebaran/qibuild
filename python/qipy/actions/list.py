#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" List all known python projects """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import operator

import qipy.parsers
import qibuild.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qibuild.parsers.cmake_build_parser(parser)


def do(args):
    """ Main Entry Point """
    python_worktree = qipy.parsers.get_python_worktree(args)
    python_projects = sorted(python_worktree.python_projects, key=operator.attrgetter("name"))
    if not python_projects:
        return
    ui.info(ui.green, "python projects in:", ui.blue, python_worktree.root)
    for project in python_projects:
        ui.info(ui.green, " * ", ui.blue, project.name, ui.reset, project.path)
