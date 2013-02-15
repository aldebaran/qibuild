## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate and load snapshot. """

from qisys import ui

import qisys

import qisrc.git
import qisrc.snapshot

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("--generate", help="Generate a snapshot file from "
                        "the current state.", action="store_true")
    parser.add_argument("--load", help="Load a snapshot on a current worktree.",
                        action="store_true")
    parser.add_argument("-f", "--force", help="Force reset even if working dir "
                        "is not clean.", action="store_true")
    parser.add_argument("-m", "--manifest", help="Use manifest instead of "
                        "current state.", action="store_true")
    parser.add_argument("-t", "--tag", help="Use a specific tag.")
    parser.add_argument("--fetch", action="store_true", default=True,
                        help="Fetch before snapshot.")
    parser.add_argument("--no-fetch", action="store_false", dest="fetch",
                        help="Do not fetch before snapshot.")
    parser.add_argument("path", help="A path to store or load informations.")

def do(args):
    """Main entry point."""

    worktree = qisys.worktree.open_worktree(args.worktree)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, worktree.root)

    if args.load:
        qisrc.snapshot.load_snapshot(worktree, args.path, args.force,
                                     fetch=args.fetch)
        return

    qisrc.snapshot.generate_snapshot(worktree, args.path,
        manifest=args.manifest, tag=args.tag, fetch=args.fetch)
