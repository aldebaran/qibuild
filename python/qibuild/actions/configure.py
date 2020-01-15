#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Configure a project. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.cmake
import qibuild.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qibuild.parsers.cmake_configure_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    if not parser.epilog:
        parser.epilog = ""
    parser.epilog += """
Note:
    if CMAKE_INSTALL_PREFIX is set during configure, it will be necessary to
    repeat it at install (for further details, see: qibuild install --help).
"""


@ui.timer("qibuild configure")
def do(args):
    """ Main entry point. """
    qibuild.parsers.convert_cmake_args_to_flags(args)
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    if args.debug_trycompile:
        ui.info(ui.green, "Using cmake --debug-trycompile")
    if args.trace_cmake:
        ui.info(ui.green, "Tracing CMake execution")
    cmake_builder.configure(clean_first=args.clean_first,
                            debug_trycompile=args.debug_trycompile,
                            trace_cmake=args.trace_cmake,
                            profiling=args.profiling,
                            summarize_options=args.summarize_options,
                            single=args.single)
