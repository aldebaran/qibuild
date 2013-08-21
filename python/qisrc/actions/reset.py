## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Reset a repository to the manifest state."""

import sys

from qisys import ui
import qisys.parsers
import qisys.worktree
import qisys.interact
import qisrc.git
import qisrc.snapshot
import qisrc.status
import qisrc.parsers

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("-f", "--force", help="If not set only a dry-run is"
                        "done.", action="store_true")
    parser.add_argument("-c", "--clean", action="store_true",
                        help="Remove untracked files and directories.")
    parser.add_argument("--fetch", action="store_true",
                        help="Fetch before reset")
    parser.add_argument("--no-fetch", action="store_false", dest="fetch",
                        help="Don't fetch before reset")
    parser.add_argument("--tag", help="Reset everything to the given tag")
    parser.add_argument("--snapshot", help="Reset everything using the given "
                        "snapshot")
    parser.set_defaults(fetch=False)

def do(args):
    """Main entry points."""

    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=True)
    snapshot = None
    if args.snapshot:
        snapshot = qisrc.snapshot.Snapshot()
        snapshot.load(args.snapshot)

    errors = list()
    for git_project in git_projects:
        state_project = qisrc.status.check_state(git_project, False)

        ui.info(ui.green, git_project.src, ui.reset, ui.bold,
                state_project.tracking)

        qisrc.status.print_state(state_project, False)

        src = git_project.src
        git = qisrc.git.Git(git_project.path)

        if args.clean:
            ui.info("Remove untracked files and directories.")
            if args.force:
                git.clean("--force", "-d", "-x")

        if not state_project.clean:
            ui.info("Clean local changes.")
            if args.force:
                git.checkout(".")

        if not git_project.default_branch:
            ui.info(git_project.src, "not in any manifest, skipping")
            continue
        branch = git_project.default_branch.name
        if state_project.incorrect_proj or state_project.not_on_a_branch:
            ui.info("Checkout", branch)
            if args.force:
                git.checkout(branch)

        if args.fetch:
            ui.info("Fetching...")
            if args.force:
                git.fetch("-a")

        to_reset = None
        if args.snapshot:
            to_reset = snapshot.sha1s.get(src)
            if not to_reset:
                ui.warning(src, "not found in the snapshot")
                continue
        elif args.tag:
            to_reset = args.tag
        else:
            to_reset = git.get_tracking_branch()

        if args.force:
            ui.info("reset", to_reset)
            try:
                git.reset("--hard", to_reset)
            except:
                errors.append(src)

    if not errors:
        return
    ui.error("Failed to reset some projects")
    for error in errors:
        ui.error(" * ", error)
    sys.exit(1)
