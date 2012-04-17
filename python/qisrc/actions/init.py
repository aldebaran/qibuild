## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os

import qibuild
import qisrc

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("manifest_url")
    parser.add_argument("manifest_name", nargs="?",
        help="Name of the manifest. Useful if you have several manifests")
    parser.add_argument("-b", "--branch", dest="branch",
        help="Use this branch for the manifest and all the projects")
    parser.set_defaults(manifest_name="default", branch="master")

def do(args):
    """Main entry point"""
    if args.worktree:
        worktree_root = args.worktree
    else:
        worktree_root = os.getcwd()
    manifest_name = "manifest/%s" % args.manifest_name
    worktree = qibuild.worktree.create(worktree_root)
    manifest_url = args.manifest_url
    branch = args.branch
    manifest = qisrc.sync.fetch_manifest(worktree,
        manifest_url, branch=branch, name=manifest_name)
    qisrc.sync.sync_projects(worktree, manifest)
    worktree.set_manifest_project(manifest_name)
