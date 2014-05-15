## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """

import qisys.parsers
import qipkg.builder

import qibuild.parsers
import qipy.parsers


def pml_parser(parser):
    qisys.parsers.build_parser(parser)
    parser.add_argument("pml_path")

def get_pml_builder(args):
    pml_path = args.pml_path
    worktree = qisys.parsers.get_worktree(args)
    build_worktree = qibuild.parsers.get_build_worktree(args)
    # here we build a CMakeBuilder from scratch becaues we won't read
    # the project names from the command line
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree)
    python_builder = qipy.parsers.get_python_builder(args)
    return qipkg.builder.PMLBuider(pml_path, cmake_builder, python_builder)
