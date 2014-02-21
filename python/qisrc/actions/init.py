## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Init a new qisrc workspace """

import os

from qisys import ui
import qisys.parsers
import qisys.worktree
import qisrc.parsers
import qisrc.worktree

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.default_parser(parser)
    qisrc.parsers.groups_parser(parser)
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
    parser.set_defaults(force=False, setup_review=True, profile="default")

def do(args):
    """Main entry point"""
    root = os.getcwd()
    if not qisys.sh.is_empty(root):
        raise Exception("Please run this command from an empty directory")
    workrtee = qisys.worktree.WorkTree(root)
    git_worktree = qisrc.worktree.GitWorkTree(workrtee)
    if args.manifest_url:
        git_worktree.configure_manifest(args.manifest_name,
                                        args.manifest_url,
                                        groups=args.groups,
                                        branch=args.branch)

    ui.info(ui.green, "New qisrc worktree initialized in",
            ui.reset, ui.bold, root)
