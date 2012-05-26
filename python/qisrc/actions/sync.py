## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize the given worktree with its manifests

 * Clone any missing project
 * Configure projects for code review

"""

import os
import operator
import logging

import qisrc
import qisrc.cmdparse
import qibuild

LOGGER = logging.getLogger(__name__)

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
        print "Updating", manifest_project.src, "..."
        git = qisrc.git.Git(manifest_project.path)
        git.pull(quiet=True)
        manifest_filename = manifest_project.profile + ".xml"
        manifest_xml = os.path.join(manifest_project.path, manifest_filename)
        qisrc.sync.init_worktree(worktree, manifest_xml, setup_review=args.setup_review)


def do(args):
    """Main entry point"""
    worktree = qisrc.open_worktree(args.worktree)
    projects = qisrc.cmdparse.projects_from_args(args)

    if len(projects) == len(worktree.projects):
        # User asked for a long operation:
        sync_all(worktree, args)

    git_projects = set()
    for project in projects:
        if project.git_project:
            git_projects.add(project.git_project)

    git_projects = list(git_projects)
    git_projects.sort(key = operator.attrgetter("src"))
    errors = list()
    project_count = len(git_projects)
    for i, project in enumerate(git_projects):
        if project_count != 1:
            LOGGER.info("Pulling project %i on %s %s", i+1, project_count, project.src)
        else:
            LOGGER.info("Pulling %s",  project.src)
        git = qisrc.git.open(project.path)
        error = git.update_branch(project.branch, project.remote)
        if error:
            errors.append((project.src, error))
    if not errors:
        return
    LOGGER.error("Fail to sync some projects")
    for (src, err) in errors:
        print src
        print "-" * len(src)
        print
        print indent(err, 2)
