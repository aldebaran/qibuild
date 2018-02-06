# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Get the list of all licenses used by the given projects """
import collections
import json

from qisys import ui
import qisys.parsers
import qibuild.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--json", action="store_true",
                        help="Output the result in JSON format")
    parser.add_argument("--oss", action="store_true",
                        help="Only dispaly non-proprietary licenses")


def do(args):
    """ Main entry point """
    cmake_builder = qibuild.parsers.get_cmake_builder(args)
    deps_solver = cmake_builder.deps_solver
    packages = deps_solver.get_dep_packages(cmake_builder.projects,
                                            ["build", "runtime", "test"])
    projects = deps_solver.get_dep_projects(cmake_builder.projects,
                                            ["build", "runtime", "test"])
    oss = args.oss

    def should_add_license(license_):
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
        print json.dumps(res, indent=2)
    else:
        for name, license_ in res.iteritems():
            ui.info(name, license_)

    return res
