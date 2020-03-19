#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Generate a binary package, ready to be used for a behavior """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qipkg.parsers
import qipkg.metapackage


def configure_parser(parser):
    """ Configure parser for this action """
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("-o", "--output")
    parser.add_argument("--with-snapshot", action="store_true", default=False)
    qipkg.parsers.pkg_parser(parser)


def do(args):
    """ Main entry point """
    output = args.output
    force = args.force
    with_snapshot = args.with_snapshot
    with_breakpad = args.with_breakpad
    with_toolchain = args.with_toolchain
    python_minify = args.python_minify
    pml_builder = qipkg.parsers.get_pml_builder(args)
    return pml_builder.package(output=output, with_breakpad=with_breakpad,
                               force=force, install_tc_packages=with_toolchain,
                               python_minify=python_minify, with_snapshot=with_snapshot)
