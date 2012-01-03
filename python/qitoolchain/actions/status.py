
## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Display the toolchains status their names, and what projects they provide

"""

import qibuild
import qitoolchain


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.cmdparse.default_parser(parser)
    parser.add_argument("name", nargs="?",
        help="Name of the toolchain to print. Default: all")


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    tc_name = args.name
    if tc_name:
        if not tc_name in qitoolchain.get_tc_names():
            print "No such toolchain: ", tc_name
            return
        toolchain = qitoolchain.Toolchain(tc_name)
        print toolchain
        return

    for tc_name in tc_names:
        toolchain = qitoolchain.Toolchain(tc_name)
        print toolchain
        print
