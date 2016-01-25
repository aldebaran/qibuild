## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
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
    parser.add_argument("--clone",
        help="Use the given worktree to do faster local clones")
    parser.set_defaults(branch="master", all=False, review=True)

def do(args):
    """Main entry point"""
    root = args.worktree or os.getcwd()
    qisys.sh.mkdir(root, recursive=True)
    worktree = qisys.worktree.WorkTree(root)
    git_worktree = qisrc.worktree.GitWorkTree(worktree)
    worktree_clone = None
    if args.clone:
        candidate_clone_path = qisys.sh.to_native_path(args.clone)
        dot_qi = os.path.join(candidate_clone_path, ".qi")
        git_xml = os.path.join(dot_qi, "git.xml")
        if not os.path.exists(git_xml):
            mess = """\
Invalid --clone argument
Worktree in {0} does not appear to be a valid qisrc worktree
({1} does not exist)
"""
            sys.exit(mess.format(args.clone, git_xml))
        candidate_worktree = qisys.worktree.WorkTree(candidate_clone_path)
        worktree_clone = qisrc.worktree.GitWorkTree(candidate_worktree)
    if args.manifest_url:
        if os.path.isdir(args.manifest_url):
            args.manifest_url = qisys.sh.to_native_path(args.manifest_url)
        ok = git_worktree.configure_manifest(args.manifest_url,
                                        groups=args.groups,
                                        branch=args.branch,
                                        review=args.review,
                                        all_repos=args.all,
                                        worktree_clone=worktree_clone)
        if not ok:
            sys.exit(1)

    ui.info(ui.green, "New qisrc worktree initialized in",
            ui.reset, ui.bold, root)
