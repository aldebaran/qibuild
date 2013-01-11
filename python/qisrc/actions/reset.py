## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Reset a repository to the manifest state."""

from qisys import ui
import qisys.parsers
import qisys.worktree
import qisys.interact
import qisrc.git
import qisrc.snapshot
import qisrc.status

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-f", "--force", help="If not set only a dry-run is"
                        "done.", action="store_true")
    parser.add_argument("-c", "--clean", action="store_true",
                        help="Remove untracked files and directories.")

def do(args):
    """Main entry points."""

    worktree = qisys.worktree.open_worktree(args.worktree)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, worktree.root)

    ui.info("Remove untracked files and directories.")
    if args.force:
        git.clean("--force", "-d", "-x")

    for project in worktree.projects:
        if not project.is_git():
            continue

        state_project = qisrc.status.check_state(project, False)

        ui.info(ui.green, project.src, ui.reset, ui.bold,
                state_project.tracking)

        qisrc.snapshot.print_state(state_project)

        git = qisrc.git.Git(project.src)

        if not state_project.clean:
            ui.info("Clean local changes.")
            if args.force:
                git.checkout(".")

        if state_project.incorrect_proj or state_project.not_on_a_branch:
            ui.info("Checkout %s" % state_project.project.branch)
            if args.force:
                git.checkout(state_project.project.branch)

        if args.force:
            git.reset("--hard", git.get_tracking_branch())
