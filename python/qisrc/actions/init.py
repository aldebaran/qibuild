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
    parser.add_argument("manifest_url", nargs="?")
    parser.add_argument("manifest_name", nargs="?",
        help="Name of the manifest. Useful if you have several manifests")
    parser.add_argument("-b", "--branch", dest="branch",
        help="Use this branch for the manifest and all the projects")
    parser.set_defaults(manifest_name="default", branch="master")
    parser.add_argument("-f", "--force", dest="force", action="store_true",
        help="By-pass some safety checks")
    parser.add_argument("--no-review", dest="setup_review", action="store_false",
        help="Do not setup code review")
    parser.set_defaults(force=False, setup_review=True)

def do(args):
    """Main entry point"""
    if args.worktree:
        worktree_root = args.worktree
        worktree_root = qibuild.sh.to_native_path(worktree_root)
    else:
        worktree_root = os.getcwd()
    manifest_src = "manifest/%s" % args.manifest_name
    worktree = qisrc.worktree.create(worktree_root, force=args.force)
    if not args.manifest_url:
        return
    manifest_url = args.manifest_url
    branch = args.branch
    manifest = qisrc.sync.fetch_manifest(worktree,
        manifest_url, branch=branch, src=manifest_src)
    qisrc.sync.sync_projects(worktree, manifest,
        update_branch=False,
        setup_review=args.setup_review)
    worktree.set_manifest_project(manifest_src,)
