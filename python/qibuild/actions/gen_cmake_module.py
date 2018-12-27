#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Generate a -config.cmake file from the contents of a directory. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.cmake.modules
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("directory")
    parser.add_argument("--name", required=True)


def do(args):
    """ Main Entry Point """
    directory = args.directory
    name = args.name
    res = qibuild.cmake.modules.generate_cmake_module(directory, name)
    ui.info(ui.green, "CMake module generated in", ui.reset, ui.bold, res)
