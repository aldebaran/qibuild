#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Deploy project(s) on a remote target.
All deployed material is installed in the location 'path' on the target 'hostname'.
Examples:
  qibuild deploy foobar --url john@mytarget:deployed
Installs everything on the target 'mytarget' in the 'deployed' directory from the 'john' 's home.
  qibuild deploy foobar --url john@mytarget:/tmp/foobar
Installs everything on the target 'mytarget' in the '/tmp/foobar' directory.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qibuild.deploy
import qibuild.parsers


def configure_parser(parser):
    """ Configure parser for this action. """
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    qisys.parsers.deploy_parser(parser)
    group = parser.add_argument_group("qibuild specific deploy options")
    group.add_argument("--split-debug", action="store_true", dest="split_debug",
                       help="split debug symbols. Enable remote debuging")
    group.add_argument("--with-tests", dest="with_tests", action="store_true",
                       help="also deploy the tests")
    group.add_argument("--no-packages", action="store_false", dest="install_tc_packages",
                       help="Do not install packages from toolchain")
    parser.set_defaults(with_tests=False, install_tc_packages=True)


def do(args):
    """ Main entry point. """
    urls = qisys.parsers.get_deploy_urls(args)
    if args.with_tests:
        default_dep_types = ["runtime", "test"]
    else:
        default_dep_types = ["runtime"]
    cmake_builder = qibuild.parsers.get_cmake_builder(
        args, default_dep_types=default_dep_types)
    for url in urls:
        cmake_builder.deploy(url, split_debug=args.split_debug,
                             with_tests=args.with_tests,
                             install_tc_packages=args.install_tc_packages)
