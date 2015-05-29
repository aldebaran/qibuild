## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Build host tools projects """

import qibuild.parsers

def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)

def do(args):
    """ Main entry point """
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    cmake_builder.build_host_tools()

