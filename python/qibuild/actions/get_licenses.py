#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Get the list of all licenses used by the given projects. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import json
import collections

import qibuild.parsers
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--json", action="store_true",
                        help="Output the result in JSON format")
    parser.add_argument("--oss", action="store_true",
                        help="Only dispaly non-proprietary licenses")


def do(args):
    """ Main entry point. """
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    deps_solver = cmake_builder.deps_solver
    packages = deps_solver.get_dep_packages(cmake_builder.projects,
                                            ["build", "runtime", "test"])
    projects = deps_solver.get_dep_projects(cmake_builder.projects,
                                            ["build", "runtime", "test"])
    oss = args.oss

    def should_add_license(license_):
        """ Should Add Licence """
        if license_ is None:
            return False
        if license_ == "proprietary" and oss:
            return False
        return True

    res = collections.OrderedDict()
    for package in packages:
        license_name = package.license
        if should_add_license(license_name):
            res[package.name] = package.license
    for project in projects:
        license_name = project.license
        if should_add_license(license_name):
            res[project.name] = project.license
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        for name, license_ in res.items():
            ui.info(name, license_)
    return res
