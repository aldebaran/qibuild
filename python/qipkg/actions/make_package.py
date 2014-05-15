## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a binary package, ready to be used for a behavior """
import qipkg.parsers

from qisys import ui
import qisys.parsers
import qipkg.parsers
import qipkg.package


def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("-o", "--output")


def do(args):
    """Main entry point"""
    output = args.output
    pml_builder = qipkg.parsers.get_pml_builder(args)
    package = qipkg.package.Package(args.pml_path)
    package.make_package(pml_builder, output=output)
