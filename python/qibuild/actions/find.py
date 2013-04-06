## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find a package

"""

import sys

from qisys import ui
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--cflags",
                        help="Outputs required compiler flags")
    parser.add_argument("--libs",
                        help="Ouputs required linnker flags")
    parser.add_argument("package")


def do(args):
    """Main entry point """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    project = qibuild.parsers.get_one_build_project(build_worktree, args)
    package = args.package

    cache = qibuild.cmake.read_cmake_cache(project.cmake_cache)
    u_package = package.upper()

    keys = cache.keys()
    keys.sort()
    keys = [k for k in keys if k.upper().startswith(package.upper())]
    if not keys:
        ui.error("Nothing found about CMake module: ", package)
        return
    ui.info("CMake module: ", package)
    for key in keys:
        value = cache[key]
        if not value:
            value = "<empty>"
        ui.info(ui.tabs(1), key, "\n",
                ui.tabs(2), value)
