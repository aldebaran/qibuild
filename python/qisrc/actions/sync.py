## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize the given worktree with its manifests

 * Clone any missing project
 * Configure projects for code review

"""

import os
import sys
import operator
import qisys.log

import qisrc
from qisrc.sync_build_profiles import sync_build_profiles
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

def indent(text, num):
    """ Indent a piece of text """
    lines = text.splitlines()
    lines = [" " * num + l for l in lines]
    return "\n".join(lines)

def sync_all(worktree, args):
    """ Fetch any manifest project, re init everything,
    re-create branch configurations, review setup and so on

    """
    manifest_projects = worktree.get_manifest_projects()
    if not manifest_projects:
        raise qisrc.manifest.NoManifest(worktree)
    # Re-synchronize everything:
    for manifest_project in manifest_projects:
        ui.info(ui.green, "Updating", manifest_project.src, "...")
        git = qisrc.git.Git(manifest_project.path)
        git.pull(quiet=True)
        manifest_filename = manifest_project.profile + ".xml"
        manifest_xml = os.path.join(manifest_project.path, manifest_filename)
        manifest = qisrc.manifest.load(manifest_xml)
        qisrc.sync.init_worktree(worktree, manifest, setup_review=args.setup_review)
        sync_build_profiles(worktree, manifest_xml)


@ui.timer("Synchronizing worktree")
def do(args):
    """Main entry point"""
    worktree = qisys.worktree.open_worktree(args.worktree)
    projects = qisrc.cmdparse.projects_from_args(args, worktree)

    if len(projects) == len(worktree.projects):
        sync_all(worktree, args)

    git_projects = set()
    for project in projects:
        if project.git_project and not project.manifest:
            git_projects.add(project.git_project)

    ui.info(ui.green, "Synchronizing projects ...")
    git_projects = list(git_projects)
    git_projects.sort(key = operator.attrgetter("src"))
    errors = list()
    project_count = len(git_projects)
    for i, project in enumerate(git_projects):
        if project_count != 1:
            ui.info(
                ui.green, "*", ui.reset, "(%2i/%2i)" %  (i+1, project_count),
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
        ui.info(indent(err, 2))
    sys.exit(1)
