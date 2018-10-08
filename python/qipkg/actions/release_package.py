# Copyright (c) 2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Update a package by replacing python source files by their byte-code equivalent """

import os

import qisys.parsers
import qipkg.release


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.default_parser(parser)
    parser.add_argument("pkg_path")
    parser.add_argument("-o", "--output")


def do(args):
    """ Main Entry Point """
    pkg_path = args.pkg_path
    output_path = args.output
    if not output_path:
        output_path = os.path.join(os.getcwd(), os.path.basename(pkg_path))
    return qipkg.release.make_release(pkg_path, output_path)
