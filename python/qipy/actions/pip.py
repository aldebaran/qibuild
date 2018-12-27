#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Run pip from the correct virtualenv """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import subprocess

import qipy.parsers
import qipy.worktree
import qibuild.parsers


def configure_parser(parser):
    """ Configure Parser """
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("pip_options", metavar="COMMAND", nargs="*")


def do(args):
    """ Main Entry Point """
    pip_options = args.pip_options
    python_builder = qipy.parsers.get_python_builder(args)
    python_worktree = python_builder.python_worktree
    pip = python_worktree.pip
    subprocess.check_call([pip] + pip_options)
