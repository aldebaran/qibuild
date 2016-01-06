## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Build all the projects of the given pml file
"""

import qisys.parsers
import qibuild.parsers
import qipkg.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    qibuild.parsers.cmake_build_parser(parser, with_build_parser=False)

def do(args):
    """Main entry point"""
    pml_builder = qipkg.parsers.get_pml_builder(args)
    pml_builder.build()
