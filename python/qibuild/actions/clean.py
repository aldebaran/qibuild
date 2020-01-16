#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Clean build directories.
By default all build directories for the current configuration
will be deleted for the specified project and its dependencies.
Use -s to clean the current project only
Use -c to choose a config
Use -f to force the clean
Use -z to clean all existing configurations
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qibuild
import qibuild.parsers
import qisys
import qisys.interact
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("-z", dest="remove_known_configs", action="store_true",
                        help="remove all build directories that match a known configuration")
    parser.add_argument("-x", dest="remove_unknown_configs", action="store_true",
                        help="remove build directories that do not match any known configuration")
    parser.add_argument("--force", "-f", dest="force", action="store_true", help="force the clean")


def _get_clean_selection(remove_known_configs, remove_unknown_configs):
    """ Get Clean Selection """
    clean_selection = "given_config"
    if remove_known_configs and remove_unknown_configs:
        clean_selection = "all_configs"
    elif remove_known_configs and not remove_unknown_configs:
        clean_selection = "known_configs"
    elif not remove_known_configs and remove_unknown_configs:
        clean_selection = "unknown_configs"
    return clean_selection


@ui.timer("qibuild clean")
def do(args):
    """ Main entry point. """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    projects = qibuild.parsers.get_build_projects(build_worktree, args,
                                                  solve_deps=True)
    clean_selection = _get_clean_selection(args.remove_known_configs, args.remove_unknown_configs)
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
            if config_name not in sorted_bdirs:
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
