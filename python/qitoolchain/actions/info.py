## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Display a complete description of a toolchain

"""

import qibuild
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?",
        help="Name of the toolchain to print. Default: all")


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    tc_name = args.name
    if tc_name:
        toolchain = qitoolchain.get_toolchain(tc_name)
        print toolchain
    else:
        for tc_name in tc_names:
            toolchain = qitoolchain.Toolchain(tc_name)
            print toolchain
            print
