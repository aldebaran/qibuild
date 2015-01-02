## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Display a complete description of a toolchain

"""

from qisys import ui
import qisys.parsers
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?",
        help="Name of the toolchain to print. Default: all")


def do(args):
    """ Main method """
    if args.name:
        tc_names = [args.name]
    else:
        tc_names = qitoolchain.get_tc_names()

    for tc_name in tc_names:
        toolchain = qitoolchain.get_toolchain(tc_name)
        ui.info(str(toolchain))
