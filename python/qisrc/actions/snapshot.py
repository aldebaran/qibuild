## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate a snapshot of all the git projects """

import os

from qisys import ui

import qisys.parsers
import qisrc.parsers
import qisrc.git
import qisrc.snapshot

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    group = parser.add_argument_group("qisrc snapshot options")
    group.add_argument("snapshot_path", nargs="?",
        help="Path to the output snapshot file. " +
        "Use `qisrc reset --force --snapshot snapshot_path` to load a snapshot" )
    group.add_argument("--deprecated-format", action="store_true",
                       help="Only used for retro-compatibility")
    parser.set_defaults(deprecated_format=False)


def do(args):
    """Main entry point."""
    git_worktree = qisrc.parsers.get_git_worktree(args)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, git_worktree.root)
    snapshot_path = args.snapshot_path
    if not snapshot_path:
        snapshot_path = os.path.join(os.getcwd(), "snapshot.json")
    qisrc.snapshot.generate_snapshot(git_worktree, snapshot_path,
                                     deprecated_format=args.deprecated_format)
    return snapshot_path
