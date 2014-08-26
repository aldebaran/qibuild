## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean a toolchain cache """

import qisys.parsers
import qitoolchain


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?", metavar="NAME",
        help="Name of the toolchain")

def do(args):
    """ Main entry point

    """
    tc = qitoolchain.get_toolchain(args.name)
    tc.clean_cache()
