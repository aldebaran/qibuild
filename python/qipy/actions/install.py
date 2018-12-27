#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Install the given python project """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qipy.parsers
import qibuild.parsers
import qisys.parsers
import qisys.command


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("dest")


def do(args):
    """ Main Entry Point """
    dest = args.dest
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    projects = qipy.parsers.get_python_projects(python_worktree, args)
    python_builder.projects = projects
    python_builder.install(dest)
