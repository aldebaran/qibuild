## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Functions to generate and load snapshot."""

import os

from qisys import ui

import qisrc.git
import qisrc.status
import qisys.interact

def generate_snapshot(worktree, path, manifest=False):
    """Generate a snapshot file."""
    if os.path.exists(path) and not os.path.isfile(path):
        return
    with open(path, 'w') as f:
        for project in worktree.projects:
            if not qisrc.git.is_git(project.path):
                continue

            # Check the state of the project and print warning.
            state_project = qisrc.status.check_state(project, False)
            print_state(state_project)

            git = qisrc.git.Git(project.path)
            if manifest:
                (returncode, sha1) = git.log("--pretty=format:%H",
                                             "-1", project.branch, raises=False)
            else:
                (returncode, sha1) = git.log("--pretty=format:%H",
                                             "-1", raises=False)

            if returncode != 0:
                ui.info(ui.red, sha1)
                continue
            f.write(project.src + ":" + sha1 + '\n')
            ui.info(ui.green, project.src, ui.reset, ui.bold, sha1)

def load_snapshot(worktree, path, force):
    """Load a snapshot file and reset projects."""
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

            state_project = qisrc.status.check_state(project, False)
            print_state(state_project)

            if not qisrc.git.is_git(project.path):
                ui.info(ui.red, src, "is not a git project.")
                continue

            git_project = qisrc.git.Git(project.path)
            if (not state_project.sync_and_clean
                   or state_project.incorrect_proj
                   or state_project.not_on_a_branch) and not force:
                ui.info(ui.red, "git reset --hard aborted.\n"
                                "Use --force to force the reset.")
                if not qisys.interact.ask_yes_no("run git reset --hard ?"):
                    continue

            git_project.reset("--hard", sha1)

def print_state(state_project):
    if not state_project.sync_and_clean:
        ui.warning(ui.red, state_project.project.src, ui.reset,
            "is not clean or sync.")

    if state_project.incorrect_proj:
        ui.warning(ui.red, state_project.project.src, ui.reset, "is on",
                ui.bold, state_project.current_branch,
                ui.reset, "but manifest is on",
                ui.bold, state_project.project.branch)

    if state_project.not_on_a_branch:
        ui.warning(ui.red, state_project.project.src, ui.reset,
            "is not on a branch.")
