## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """

from qisys import ui
import qisys.parsers
import qipkg.parsers
import qipkg.metapackage
import qipkg.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("-o", "--output")
    parser.add_argument("--with-breakpad", action="store_true")
    parser.set_defaults(with_breakpad=False)


def do(args):
    """Main entry point"""
    output = args.output
    with_breakpad = args.with_breakpad
    pml_builder = qipkg.parsers.get_pml_builder(args)
    return pml_builder.package(output=output, with_breakpad=with_breakpad)
