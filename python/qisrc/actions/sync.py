## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize a worktree with a manifest:
update every repository, clone any new repository

"""

import logging

import qisrc
import qibuild

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)
    parser.add_argument("--rebase", action="store_true", dest="rebase",
        help="Use git pull --rebase")
    parser.add_argument("-b", "--branch", dest="branch",
        help="Use this branch for the manifest and all the projects")
    parser.set_defaults(rebase=False, branch="master")


def do(args):
    """Main entry point"""
    worktree = qibuild.open_worktree(args.worktree)
    manifest_urls = worktree.get_manifest_urls()
    if not manifest_urls:
        mess  = "No manifest url found.\n"
        mess += "Try calling `qisrc init`"
        raise Exception(mess)

    branch = args.branch
    rebase = args.rebase
    for manifest_url in manifest_urls:
        manifest = qisrc.sync.fetch_manifest(worktree, manifest_url, branch=branch)
        qisrc.sync.clone_missing(worktree, manifest)

    qisrc.sync.pull_projects(worktree, rebase=args.rebase)
