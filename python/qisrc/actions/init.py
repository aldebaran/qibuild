## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os

import qisys
import qisrc
from qisrc.sync_build_profiles import sync_build_profiles

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("manifest_url", nargs="?")
    parser.add_argument("manifest_name", nargs="?",
        help="Name of the manifest. Useful if you have several manifests")
    parser.add_argument("-b", "--branch", dest="branch",
        help="Use this branch for the manifest and all the projects")
    parser.add_argument("-p", "--profile", dest="profile",
        help="Use the given profile. Assume <profile>.xml exists")
    parser.set_defaults(manifest_name="default", branch="master")
    parser.add_argument("-f", "--force", dest="force", action="store_true",
        help="By-pass some safety checks")
    parser.add_argument("--no-review", dest="setup_review", action="store_false",
        help="Do not setup code review")
    parser.set_defaults(force=False, setup_review=True, profile="default")

def do(args):
    """Main entry point"""
    if args.worktree:
        worktree_root = args.worktree
        worktree_root = qisys.sh.to_native_path(worktree_root)
    else:
        worktree_root = os.getcwd()
    manifest_src = "manifest/%s" % args.manifest_name
    worktree = qisys.worktree.create(worktree_root, force=args.force)
    if not args.manifest_url:
        return
    manifest_url = args.manifest_url
    branch = args.branch
    if not manifest_url:
        return worktree
    manifest_is_a_regular_file = False
    qisys.ui.info(qisys.ui.green, "initializing worktree:",
                    qisys.ui.blue, worktree_root,
                    qisys.ui.green, "using profile:",
                    qisys.ui.blue, args.profile)
    if os.path.isfile(manifest_url):
        manifest_file = manifest_url
        manifest_is_a_regular_file = True
    else:
        manifest_file = qisrc.sync.fetch_manifest(worktree,
            manifest_url, branch=branch, src=manifest_src,
            profile=args.profile)
    manifest = qisrc.manifest.load(manifest_file)
    qisrc.sync.init_worktree(worktree, manifest, setup_review=args.setup_review)
    sync_build_profiles(worktree, manifest_file)
    if not manifest_is_a_regular_file:
        worktree.set_manifest_project(manifest_src, args.profile)
    return worktree
