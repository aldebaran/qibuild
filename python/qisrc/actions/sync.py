## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize a worktree with a manifest:
update every repository, clone any new repository

"""

import os
import logging

import qisrc
import qibuild

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--no-update-branch", dest="update_branch", action="store_false",
        help="Do not try to update local branches")
    parser.add_argument("--no-review", dest="setup_review", action="store_false",
        help="Do not setup projects for review")
    parser.set_defaults(rebase=False, update_branch=True, setup_review=True)


def do(args):
    """Main entry point"""
    worktree = qisrc.open_worktree(args.worktree)
    manifest_projects = worktree.get_manifest_projects()
    if not manifest_projects:
        mess  = "Could not find any manifest project for worktree in %s \n" % worktree.root
        mess += "Try calling `qisrc init MANIFEST_URL`"
        raise Exception(mess)

    for manifest_project in manifest_projects:
        git = qisrc.git.Git(manifest_project.path)
        git.pull(quiet=True)
        manifest_xml = os.path.join(manifest_project.path, "manifest.xml")
        qisrc.sync.sync_projects(worktree, manifest_xml,
            update_branch=args.update_branch,
            setup_review=args.setup_review)
