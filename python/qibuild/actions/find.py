#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Find a package. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qibuild.find
import qibuild.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--cflags",
                        help="Outputs required compiler flags")
    parser.add_argument("--libs",
                        help="Ouputs required linnker flags")
    parser.add_argument("--cmake", dest="cmake", action="store_true",
                        help="Search in cmake cache")
    parser.add_argument("package")


def _use_cmake_cache(args):
    """
    Use cmake cache to get informations about searched package.
    Mandatory to find package dependencies or include dir.
    """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    project = qibuild.parsers.get_one_build_project(build_worktree, args)
    package = args.package
    cache = qibuild.cmake.read_cmake_cache(project.cmake_cache)
    keys = sorted(cache.keys())
    keys = [k for k in keys if k.upper().startswith(package.upper())]
    if not keys:
        ui.error("Nothing found about CMake module: ", package)
        sys.exit(1)
    ui.info("CMake module: ", package)
    for key in keys:
        value = cache[key]
        if not value:
            value = "<empty>"
        ui.info(ui.tabs(1), key, "\n",
                ui.tabs(2), value)


def _use_build_directories(args):
    """ Print packages found with find(). """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    projects = qibuild.parsers.get_build_projects(build_worktree,
                                                  args,
                                                  default_all=True)
    debug = build_worktree.build_config.debug
    found = qibuild.find.find([p.sdk_directory for p in projects],
                              args.package, debug=debug, expect_one=False)
    if not found:
        sys.exit(1)
    for res in found:
        ui.info(res)


def do(args):
    """ Main entry point. """
    if args.cmake:
        _use_cmake_cache(args)
    else:
        _use_build_directories(args)
