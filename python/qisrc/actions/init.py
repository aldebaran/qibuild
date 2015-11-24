## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os
import sys

from qisys import ui
import qisys.sh
import qisys.parsers
import qisys.worktree
import qisrc.parsers
import qisrc.worktree

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisrc.parsers.groups_parser(parser)
    parser.add_argument("manifest_url", nargs="?")
    parser.add_argument("-b", "--branch", dest="branch",
        help="Use this branch for the manifest")
    parser.add_argument("--no-review", dest="review", action="store_false",
        help="Do not sync the review remotes")
    parser.add_argument("--all", dest="all", action="store_true",
        help="Do not use the default group, and clone all the projects "
             "of the manifest")
    parser.set_defaults(branch="master", all=False, review=True)

def do(args):
    """Main entry point"""
    root = args.worktree or os.getcwd()
    qisys.sh.mkdir(root, recursive=True)
    worktree = qisys.worktree.WorkTree(root)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    if args.manifest_url:
        if os.path.isdir(args.manifest_url):
            args.manifest_url = qisys.sh.to_native_path(args.manifest_url)
        ok = git_worktree.configure_manifest(args.manifest_url,
                                        groups=args.groups,
                                        branch=args.branch,
                                        review=args.review,
                                        all_repos=args.all)
        if not ok:
            sys.exit(1)

    ui.info(ui.green, "New qisrc worktree initialized in",
            ui.reset, ui.bold, root)
