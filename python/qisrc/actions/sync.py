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
    parser.add_argument("--rebase", action="store_true", dest="rebase",
        help="Use git pull --rebase")
    parser.set_defaults(rebase=False)


def do(args):
    """Main entry point"""
    worktree = qisrc.open_worktree(args.worktree)
    manifest_projects = worktree.get_manifest_projects()
    if not manifest_projects:
        mess  = "Could not find any manifest project for worktree in %s \n" % worktree.root
        mess += "Try calling `qisrc init`"
        raise Exception(mess)

    for manifest_project in manifest_projects:
        manifest_xml = os.path.join(manifest_project.path, "manifest.xml")
        qisrc.sync.sync_projects(worktree, manifest_xml)

    qisrc.sync.pull_projects(worktree, rebase=args.rebase)
