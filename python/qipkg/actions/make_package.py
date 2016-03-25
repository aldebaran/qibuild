## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
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
    parser.add_argument("--no-toolchain-packages", dest="include_tc_packages",
                        action="store_false",
                        help="Do not include packages from the toolchain.\n"
                             "Warning: your .pkg may no longer be compatible "
                             "with other releases of NAOqi")
    qipkg.parsers.pkg_parser(parser)
    parser.set_defaults(include_tc_packages=True)


def do(args):
    """Main entry point"""
    output = args.output
    with_breakpad = args.with_breakpad
    force = args.force
    include_tc_packages = args.include_tc_packages
    pml_builder = qipkg.parsers.get_pml_builder(args)
    return pml_builder.package(output=output,
                              with_breakpad=with_breakpad,
                              force=force,
                              include_tc_packages=include_tc_packages)
