#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Install all the projects to the given dest """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.sh
import qisys.parsers
import qipkg.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qipkg.parsers.pml_parser(parser)
    parser.add_argument("--pkg", action="store_true", dest="pkg",
                        help="Generate and install .pkg files")
    parser.add_argument("dest")
    parser.set_defaults(pkg=False)


def do(args):
    """ Main entry point """
    pml_builder = qipkg.parsers.get_pml_builder(args)
    dest = args.dest
    if args.pkg:
        qisys.sh.mkdir(dest, recursive=True)
        packages = pml_builder.package()
        for package in packages:
            qisys.sh.install(package, dest)
    else:
        pml_builder.install(dest)
