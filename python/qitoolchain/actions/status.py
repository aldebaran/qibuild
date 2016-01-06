## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Deprecated : Use `qitoolchain list` or `qitoolchain info`

"""

import qisys

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)
    parser.add_argument("name", nargs="?",
        help="Name of the toolchain to print. Default: all")
    parser.add_argument("--list", action="store_true",
        help="Display a list of known toolchains")


def do(args):
    """ Main method """
    print "`qitoolchain status` is deprecated"
    print "use `qitoolchain list` or `qitoolchain info` instead"
    if args.list:
        qisys.script.run_action("qitoolchain.actions.list",
            forward_args=args)
    else:
        qisys.script.run_action("qitoolchain.actions.info",
            forward_args=args)
