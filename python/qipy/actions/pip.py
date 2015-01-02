## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Run pip from the correct virtualenv

"""

import sys
import os
import subprocess

from qisys import ui
import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("pip_options", metavar="COMMAND", nargs="*")

def do(args):
    pip_options = args.pip_options
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    pip = python_worktree.pip
    subprocess.check_call([pip] + pip_options)
