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
import qibuild.log

import qisrc
from qisrc.sync_build_profiles import sync_build_profiles
import qisrc.cmdparse
import qibuild
from qibuild import ui


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)
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
        qisrc.sync.init_worktree(worktree, manifest_xml, setup_review=args.setup_review)
        sync_build_profiles(worktree, manifest_xml)


def do(args):
    """Main entry point"""
    worktree = qisrc.open_worktree(args.worktree)
    projects = qisrc.cmdparse.projects_from_args(args)

    should_fetch_first = True
    if len(projects) == len(worktree.projects):
        sync_all(worktree, args)
        should_fetch_first = False

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
        git = qisrc.git.open(project.path)
        error = git.update_branch(project.branch, project.remote,
                                 fetch_first=True)
        if error:
            errors.append((project.src, error))
    if not errors:
        return
    print
    ui.error("Fail to sync some projects")
    for (src, err) in errors:
        ui.info(ui.blue, src)
        print "-" * len(src)
        print indent(err, 2)
    sys.exit(1)
