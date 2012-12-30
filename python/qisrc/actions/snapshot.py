## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Generate and load snapshot. """

import os

from qisys import ui

import qisys

import qisrc.git

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("--generate", help="Generate a snapshot file from "
                        "the current state.", action="store_true")
    parser.add_argument("--load", help="Load a snapshot on a current worktree.",
                        action="store_true")
    parser.add_argument("-f", "--force", help="Force reset even if working dir "
                        "is not clean.", action="store_true")
    parser.add_argument("path", help="A path to store or load informations.")

def do(args):
    """Main entry point."""

    worktree = qisys.worktree.open_worktree(args.worktree)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, worktree.root)

    if args.load:
        load_snapshot(worktree, args.path, args.force)
        return

    generate_snapshot(worktree, args.path)

def generate_snapshot(worktree, path):
    if os.path.exists(path) and not os.path.isfile(path):
        return
    with open(path, 'w') as f:
        for project in worktree.projects:
            if not project.is_git():
                continue
            git = qisrc.git.Git(project.path)
            (returncode, sha1) = git.log("--pretty=format:%H", "-1", raises=False)
            if returncode != 0:
                ui.info(ui.red, sha1)
                continue
            f.write(project.src + ":" + sha1 + '\n')
            ui.info(ui.green, project.src, ui.reset, ui.bold, sha1)

def load_snapshot(worktree, path, force):
    if not os.path.isfile(path):
        return
    with open(path, 'r') as f:
        for line in f:
            (src, sha1) = line.split(":")
            src = src.strip()
            sha1 = sha1.strip()
            ui.info(ui.green, src, sha1)

            project = worktree.get_project(src)

            if project is None:
                ui.info(ui.red, src, "is not a project.")
                continue

            if not project.is_git():
                ui.info(ui.red, src, "is not a git project.")
                continue

            git_project = qisrc.git.Git(project.path)
            if not git_project.is_clean() and not force:
                ui.info(ui.red, project.src, "is not clean, reset --hard aborted.\n"
                        "Use --force to force the reset.")
                continue
            git_project.reset("--hard", sha1)
