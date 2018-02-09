# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Install the given python project """
import qisys.command

import qisys.parsers
import qipy.parsers
import qibuild.parsers


def configure_parser(parser):
    qisys.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("dest")


def do(args):
    dest = args.dest
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    projects = qipy.parsers.get_python_projects(python_worktree, args)
    python_builder.projects = projects
    python_builder.install(dest)
