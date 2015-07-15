## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Return the path to the activate file in the virtualenv

Mostly useful in scripts:

    source $(qibuild sourceme)
"""

from qisys import ui

import qisys.parsers
import qipy.parsers
import qibuild.parsers

def configure_parser(parser):
    qisys.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)

def do(args):
    python_builder = qipy.parsers.get_python_builder(args)
    res = python_builder.python_worktree.bin_path("activate")
    print res
    return res
