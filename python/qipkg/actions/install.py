# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Install all the projects to the given dest
"""

import qisys.parsers
import qisys.sh
import qipkg.parsers


def configure_parser(parser):
    """Configure parser for this action"""
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("--pkg", action="store_true", dest="pkg",
                        help="Generate and install .pkg files")
    parser.add_argument("dest")
    parser.set_defaults(pkg=False)


def do(args):
    """Main entry point"""
    pml_builder = qipkg.parsers.get_pml_builder(args)
    dest = args.dest
    if args.pkg:
        qisys.sh.mkdir(dest, recursive=True)
        packages = pml_builder.package()
        for package in packages:
            qisys.sh.install(package, dest)
    else:
        pml_builder.install(dest)
