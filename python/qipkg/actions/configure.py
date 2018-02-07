# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Configure all the projects of the given pml file
"""

import qibuild.parsers
import qipkg.parsers


def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    qibuild.parsers.cmake_configure_parser(parser)


def do(args):
    """Main entry point"""
    qibuild.parsers.convert_cmake_args_to_flags(args)
    pml_builder = qipkg.parsers.get_pml_builder(args)
    pml_builder.configure()
