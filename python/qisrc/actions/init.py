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

def do(args):
    """Main entry point"""
    if args.worktree:
        worktree_root = args.worktree
    else:
        worktree_root = os.getcwd()
    worktree = qibuild.worktree.create(worktree_root)
    manifest_url = args.manifest_url
    manifest = qisrc.sync.fetch_manifest(worktree, manifest_url)
    qisrc.sync.clone_missing(worktree, manifest)
    worktree.add_manifest_url(manifest_url)
