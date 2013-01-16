## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean build directories.

By default all build directories for the current configuration
will be deleted for the specified project and its dependencies.

Use -s to clean the current project only
Use -c to choose a config
Use -f to force the clean
"""

import os

import qisys
from qisys import ui
import qibuild
import qibuild.cmdparse

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the clean")

def get_build_dirs(projects):
    """ Returns a list of existing build directories """
    bdirs = []
    for project in projects:
        if os.path.isdir(project.build_directory):
            bdirs.append(project.build_directory)
    return bdirs

@ui.timer("qibuild clean")
def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args.worktree, args)
    (_, projects) = qibuild.cmdparse.deps_from_args(toc, args)

    bdirs = get_build_dirs(projects)
    bdir_count = len(bdirs)

    if bdir_count == 0:
        ui.info(ui.green, "No directories to clean")
    elif not args.force:
        ui.info(ui.green, "Build directories that will be removed", ui.reset, ui.bold, "(use -f to apply):")

    for i, bdir in enumerate(bdirs):
        if args.force:
            ui.info(ui.green, "*", ui.reset,
                "(%i/%i)" % (i+1, bdir_count),
                ui.green, "Cleaning", ui.reset, bdir)

            # delete the build directory
            qisys.sh.rm(bdir)
        else:
            ui.info(ui.green, "*", ui.reset,
                "(%i/%i)" % (i+1, bdir_count),
                ui.reset, bdir)
