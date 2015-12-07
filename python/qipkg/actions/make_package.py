## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """

from qisys import ui
import qisys.parsers
import qipkg.parsers
import qipkg.metapackage

def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("-o", "--output")
    qipkg.parsers.pkg_parser(parser)


def do(args):
    """Main entry point"""
    output = args.output
    with_breakpad = args.with_breakpad
    force = args.force
    pml_builder = qipkg.parsers.get_pml_builder(args)
    return pml_builder.package(output=output, with_breakpad=with_breakpad, force=force)
