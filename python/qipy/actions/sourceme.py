#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Return the path to the activate file in the virtualenv.
Mostly useful in scripts:
    source $(qibuild sourceme)
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qipy.parsers
import qisys.parsers
import qibuild.parsers


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)


def do(args):
    """ Main Entry Point """
    python_builder = qipy.parsers.get_python_builder(args)
    res = python_builder.python_worktree.bin_path("activate")
    print(res)
    return res
