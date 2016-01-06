## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Remove a complete virtualenv

"""
import sys
import os

from qisys import ui
import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("-f", "--force", dest="force", action="store_true")

def do(args):
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    venv_path = python_worktree.venv_path
    if not args.force:
        ui.info("Would delete", venv_path)
    else:
        ui.info("Removing", venv_path)
        qisys.sh.rm(venv_path)
