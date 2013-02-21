## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the state of all git repositories and exit
"""

import sys

from qisys import ui
import qisys
import qisrc
import qisrc.status


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("--untracked-files", "-u",
        dest="untracked_files",
        action="store_true",
        help="display untracked files")
    parser.add_argument("--show-branch", "-b",
        dest="show_branch",
        action="store_true",
        help="display branch and tracking branch for each repository")

def do(args):
    """Main method."""
    qiwt = qisys.worktree.open_worktree(args.worktree)

    git_projects = qisrc.git.get_git_projects(qiwt.projects)
    manifests = qiwt.get_manifest_projects()
    git_projects = list(set(git_projects) - set(manifests))

    num_projs = len(git_projects)
    max_len = max([len(p.src) for p in git_projects])
    state_projects = list()

    for (i, git_project) in enumerate(git_projects, start = 1):
        if sys.stdout.isatty():
            src = git_project.src
            to_write = "Checking (%d/%d) " % (i, num_projs)
            to_write += src.ljust(max_len)
            sys.stdout.write(to_write + "\r")
            sys.stdout.flush()

        state_project = qisrc.status.check_state(git_project, args.untracked_files)

        if args.show_branch or not state_project.sync_and_clean:
            state_projects.append(state_project)

    if sys.stdout.isatty():
        ui.info("Checking (%d/%d):" % (num_projs, num_projs), "done",
                " " * max_len)

    dirty = [x for x in state_projects if not x.sync_and_clean]
    ui.info("\n", ui.brown, "Dirty projects", len(dirty), "/", num_projs)

    for git_project in state_projects:
        qisrc.status.print_state(git_project, max_len)

    max_len = max([max_len, len("Project")])
    qisrc.status.print_incorrect_projs(state_projects, max_len)

    qisrc.status.print_not_on_a_branch(state_projects)

    if not args.untracked_files:
        ui.info("Tips: use -u to show untracked files")

