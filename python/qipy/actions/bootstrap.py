#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Make all python projects available in the current build configuration """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qipy.parsers
import qipy.worktree
import qibuild.parsers


def configure_parser(parser):
    """ Configure Parser """
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("requirements", nargs="*")
    parser.add_argument("--no-site-packages", action="store_false",
                        dest="site_packages",
                        help="Do not allow access to global `site-packages` "
                             "directory")
    parser.add_argument("-p", "--python",
                        help="The Python interpreter to use")
    parser.set_defaults(requirements=["pip", "virtualenv", "ipython"],
                        site_packages=True)


def do(args):
    """ Main Entry Point """
    python_builder = qipy.parsers.get_python_builder(args)
    ok = python_builder.bootstrap(remote_packages=args.requirements,
                                  site_packages=args.site_packages,
                                  python_executable=args.python)
    if not ok:
        sys.exit(1)
