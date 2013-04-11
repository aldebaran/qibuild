## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Clean build directories.

By default all build directories for the current configuration
will be deleted for the specified project and its dependencies.

Use -s to clean the current project only
Use -c to choose a config
Use -f to force the clean
Use -z to clean all existing configurations
"""

import os

import qisys
from qisys import ui
import qibuild
import qibuild.cmdparse

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("-z", dest="all_toolchains", action="store_true",
                                                help="erase for all toolchains")
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the clean")

def only_existing_dirs(dirs):
    """Return a list of existing directories from a list of dirs."""
    existing_dirs = [x for x in dirs if os.path.isdir(x)]
    return existing_dirs

def get_build_dirs(projects):
    """Returns a list of build directories."""
    bdirs = [project.build_directory for project in projects]
    return bdirs

@ui.timer("qibuild clean")
def do(args):
    """Main entry point."""
    toc = qibuild.toc.toc_open(args.worktree, args)
    (_, projects) = qibuild.cmdparse.deps_from_args(toc, args)

    if args.all_toolchains:
        bdirs = list()
        for project in projects:
            dirs = os.listdir(project.path)
            bdirs.extend([os.path.join(project.path, x) for x in dirs if
                os.path.isdir(os.path.join(project.path, x)) and
                                      qibuild.project.is_build_dir(project, x)])
    else:
        bdirs = get_build_dirs(projects)

    bdirs = only_existing_dirs(bdirs)
    bdir_count = len(bdirs)

    if bdir_count == 0:
        ui.info(ui.green, "No directory to clean")
    elif not args.force:
        ui.info(ui.green, "Build directories that will be removed", ui.reset, ui.bold, "(use -f to apply):")

    for i, bdir in enumerate(bdirs, start=1):
        to_print = [ui.green, "*", ui.reset, "(%i/%i)" % (i, bdir_count)]
        if args.force:
            to_print.extend([ui.green, "Cleaning", ui.reset, bdir])

            # delete the build directory
            qisys.sh.rm(bdir)
        else:
            to_print.extend([ui.reset, bdir])
        ui.info(*to_print)
