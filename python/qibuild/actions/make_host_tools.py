# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Build host tools projects """

import qibuild.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.cmake_configure_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("-a", "--all", action="store_true",
                        help="Build every host project")
    parser.add_argument("projects", nargs="*", metavar="PROJECT",
                        help="Project name(s)")


def do(args):
    """ Main entry point """
    host_builder = qibuild.parsers.get_host_tools_builder(args)
    host_builder.configure()
    host_builder.build()
