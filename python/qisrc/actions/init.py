## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os

import qibuild
import qisrc
from qisrc.sync_build_profiles import sync_build_profiles

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("manifest_url")
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
        worktree_root = qibuild.sh.to_native_path(worktree_root)
    else:
        worktree_root = os.getcwd()
    manifest_src = "manifest/%s" % args.manifest_name
    worktree = qisrc.worktree.create(worktree_root, force=args.force)
    if not args.manifest_url:
        return
    manifest_url = args.manifest_url
    branch = args.branch
    if not manifest_url:
        return worktree
    manifest_is_a_regular_file = False
    qibuild.ui.info(qibuild.ui.green, "initializing worktree:",
                    qibuild.ui.blue, worktree_root,
                    qibuild.ui.green, "using profile:",
                    qibuild.ui.blue, args.profile)
    if os.path.isfile(manifest_url):
        manifest = manifest_url
        manifest_is_a_regular_file = True
    else:
        manifest = qisrc.sync.fetch_manifest(worktree,
            manifest_url, branch=branch, src=manifest_src,
            profile=args.profile)
    qisrc.sync.init_worktree(worktree, manifest, setup_review=args.setup_review)
    sync_build_profiles(worktree, manifest)
    if not manifest_is_a_regular_file:
        worktree.set_manifest_project(manifest_src, args.profile)
    return worktree
