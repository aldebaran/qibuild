## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize the given worktree with its manifests

 * Clone any missing project
 * Configure projects for code review

"""

import os
import sys
import qisys.log

import qisrc
import qisrc.parsers
import qisrc.cmdparse
import qibuild.parsers
import qibuild
from qisys import ui


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    qisrc.parsers.groups_parser(parser)

    parser.add_argument("--no-review", dest="setup_review", action="store_false",
        help="Do not setup projects for review")
    parser.set_defaults(setup_review=True)

@ui.timer("Synchronizing worktree")
def do(args):
    """Main entry point"""
    worktree = qisys.worktree.open_worktree(args.worktree)
    projects = qisrc.cmdparse.projects_from_args(args, worktree)

    if len(projects) == len(worktree.projects):
        qisrc.sync.sync_all(worktree, args)

    ui.info(ui.green, "Synchronizing projects ...")
    git_projects = qisrc.sync.get_toplevel_git_projects(projects)

    errors = list()
    project_count = len(git_projects)

    for i, project in enumerate(git_projects, start=1):
        if project_count != 1:
            ui.info(
                ui.green, "*", ui.reset, "(%2i/%2i)" % (i, project_count),
                ui.blue, project.src)
        else:
            ui.info(ui.bold, "Pulling", ui.blue, project.src)

        git = qisrc.git.Git(project.path)
        error = git.update_branch(project.branch, project.remote,
                                 fetch_first=True)
        if error:
            errors.append((project.src, error))

    if not errors:
        return

    ui.error("Fail to sync some projects")
    for (src, err) in errors:
        ui.info(ui.blue, src)
        ui.info("-" * len(src))
        ui.info(ui.indent(err, num=2))
    sys.exit(1)
