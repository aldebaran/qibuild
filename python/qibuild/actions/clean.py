## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
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
import qisys.interact
import qibuild
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("-z", dest="remove_known_configs", action="store_true",
                        help="remove all build directories that match a known configuration")
    parser.add_argument("-x", dest="remove_unknown_configs", action="store_true",
                        help="remove build directories that do not match any known configuration")
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the clean")

@ui.timer("qibuild clean")
def do(args):
    """Main entry point."""
    build_worktree = qibuild.parsers.get_build_worktree(args)
    projects = qibuild.parsers.get_build_projects(build_worktree, args,
                                                  solve_deps=True)

    if args.remove_known_configs and args.remove_unknown_configs:
        clean_selection= "all_configs"
    elif args.remove_known_configs and not args.remove_unknown_configs:
        clean_selection = "known_configs"
    elif not args.remove_known_configs and args.remove_unknown_configs:
        clean_selection = "unknown_configs"
    else:
        clean_selection = "given_config"

    bdirs = {'known_configs': list(), 'unknown_configs': list()}
    all_configs = clean_selection != "given_config"
    for project in projects:
        bdirs_ = project.get_build_dirs(all_configs=all_configs)
        for cat in bdirs_.keys():
            bdirs[cat].extend(bdirs_[cat])

    if clean_selection in ["given_config", "all_configs", "known_configs"]:
        bdir_count = len(bdirs['known_configs'])
        if bdir_count == 0:
            ui.info(ui.green, "No build directory to clean")
        elif not args.force:
            ui.info(ui.green, "Build directories that will be removed",
                ui.reset, ui.bold, "(use -f to apply):")
        for i, bdir in enumerate(bdirs['known_configs']):
            message = list()
            if args.force:
                message.extend([ui.green, "Cleaning", ui.reset, bdir])

                # delete the build directory
                qisys.sh.rm(bdir)
            else:
                message.append(bdir)
            ui.info_count(i, bdir_count, *message)

    if clean_selection in ["all_configs", "unknown_configs"]:
        bdir_count = len(bdirs['unknown_configs'])
        if bdir_count == 0:
            ui.info(ui.green, "No build directory matching unknown configuration to clean")
        elif not args.force:
            ui.info(ui.green, "Build directories matching unknown configuration that may be removed",
                ui.reset, ui.bold, "(interactive mode, use -f to apply):")
        # remove uncertain build directories, by configuration name, so sort them
        sorted_bdirs = {}
        for bdir in bdirs['unknown_configs']:
            # all build directory names should be prefixed with "build-", so strip it
            config_name = os.path.basename(bdir)[6:]
            if not config_name in sorted_bdirs:
                sorted_bdirs[config_name] = []
            sorted_bdirs[config_name].append(bdir)
        for c, sbdirs in sorted_bdirs.items():
            question = "Remove build directories matching the '%s' configuration?" % c
            answer = qisys.interact.ask_yes_no(question, default=False)
            if not answer:
                continue
            bdir_count = len(sbdirs)
            for i, bdir in enumerate(sbdirs, start=1):
                to_print = [ui.green, "*", ui.reset, "(%i/%i)" % (i, bdir_count)]
                if args.force:
                    to_print.extend([ui.green, "Cleaning", ui.reset, bdir])

                    # delete the build directory
                    qisys.sh.rm(bdir)
                else:
                    to_print.extend([ui.reset, bdir])
                ui.info(*to_print)

