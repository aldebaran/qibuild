## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Initialize a new qibuild worktree """

import argparse
import os

from qisys import ui
import qisys.worktree
import qibuild.parsers
import qibuild.worktree


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    # backward-compat:
    parser.add_argument("-c", "--config", help=argparse.SUPPRESS)
    parser.add_argument("--interactive", action="store_true",
                        help=argparse.SUPPRESS)
    parser.set_defaults(interactive=False)

def do(args):
    """Main entry point"""
    root = args.worktree or os.getcwd()
    if os.path.exists(os.path.join(root, '.qi')):
        raise Exception("A .qi directory already exists here. " +
                        "Please remove it or initialize elsewhere.")
    worktree = qisys.worktree.WorkTree(root)
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    if args.config:
        ui.warning("`qibuild init -c` is deprecated", "\n",
                   "Use `qitoolchain set-default` instead")
        qisys.script.run_action("qitoolchain.actions.set_default",
                                [args.config, "--worktree", build_worktree.root])
    if args.interactive:
        ui.warning("`qibuild init --interactive` is deprecated", "\n",
                   "Use `qibuild config --wizard` instead")
        qisys.script.run_action("qibuild.actions.config",
                               ["--wizard", "--worktree", build_worktree.root])
