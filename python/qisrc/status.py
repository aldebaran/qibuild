# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

"""A set of function to know the status of a git repository."""

import qisrc.git
from qisys import ui


def stat_tracking_remote(git, branch, tracking):
    """Check if branch is ahead and / or behind tracking."""
    if branch is None or tracking is None:
        return 0, 0
    _, local_ref = git.call("rev-parse", branch, raises=False)
    _, remote_ref = git.call("rev-parse", tracking, raises=False)
    return stat_ahead_behind(git, local_ref, remote_ref)


def stat_fixed_ref(git, remote_ref):
    """ Check is HEAD is and and / or behind given ref. """
    _, local_ref = git.call("rev-parse", "HEAD", raises=False)
    return stat_ahead_behind(git, local_ref, remote_ref)


def stat_ahead_behind(git, local_ref, remote_ref):
    """ Returns a tuple (ahead, behind) describing how far
    from the remote ref the local ref is

    """
    behind = 0
    ahead = 0
    (ret, out) = git.call("rev-list", "--left-right",
                          "%s..%s" % (remote_ref, local_ref), raises=False)
    if ret == 0:
        ahead = len(out.split())
    (ret, out) = git.call("rev-list", "--left-right",
                          "%s..%s" % (local_ref, remote_ref), raises=False)
    if ret == 0:
        behind = len(out.split())
    return ahead, behind


class ProjectState(object):  # pylint: disable=too-many-instance-attributes
    """A class which represent a project and is cleanlyness."""

    def __init__(self, project):
        self.project = project
        self.fixed_ref = None
        self.not_on_a_branch = False
        self.incorrect_proj = False
        self.clean = True
        self.ahead = 0
        self.behind = 0
        self.ahead_manifest = 0
        self.behind_manifest = 0
        self.current_branch = None
        self.tracking = None
        self.valid = True
        self.status = None
        self.manifest_branch = None

    @property
    def sync(self):
        """Tell if project is synced."""
        return self.ahead == 0 and self.behind == 0

    @property
    def sync_and_clean(self):
        """Tell if project is synced and if it's clean."""
        return self.clean and self.sync


def check_state(project, untracked):
    """Check and register the state of a project."""
    state_project = ProjectState(project)

    git = qisrc.git.Git(project.path)

    if not git.is_valid():
        state_project.valid = False
        return state_project

    state_project.clean = git.is_clean(untracked=untracked)
    if project.fixed_ref:
        state_project.ahead, state_project.behind = stat_fixed_ref(git, project.fixed_ref)
        state_project.fixed_ref = project.fixed_ref
        _set_status(git, state_project, untracked=untracked)
        return state_project

    state_project.current_branch = git.get_current_branch()
    state_project.tracking = git.get_tracking_branch()
    if project.default_remote and project.default_branch:
        state_project.manifest_branch = "%s/%s" % (project.default_remote.name, project.default_branch.name)

    if state_project.current_branch is None:
        state_project.not_on_a_branch = True
        return state_project

    if project.default_branch:
        if state_project.current_branch != project.default_branch.name:
            state_project.incorrect_proj = True

    (state_project.ahead, state_project.behind) = stat_tracking_remote(
        git,
        state_project.current_branch,
        state_project.tracking)
    if state_project.incorrect_proj:
        (state_project.ahead_manifest, state_project.behind_manifest) = stat_tracking_remote(
            git, state_project.current_branch, "%s/%s" % (
                project.default_remote.name, project.default_branch.name))

        _set_status(git, state_project, untracked=untracked)
    return state_project


def _set_status(git, state_project, untracked=False):
    """ When project is not clean, display git status
    (untracked files and the like)

    """
    if not state_project.sync_and_clean:
        out = git.get_status(untracked)
        if out is not None:
            state_project.status = [x for x in out.splitlines() if x.strip()]


def _print_behind_ahead(behind, ahead):
    numcommits = ""
    if behind:
        numcommits += "-" + str(behind)
    if behind and ahead:
        numcommits += "/"
    if ahead:
        numcommits += "+" + str(ahead)
    return numcommits


def print_state(project, max_len):
    """Print a state project."""
    if project.valid:
        if project.ahead or project.behind:
            numcommits = _print_behind_ahead(project.behind, project.ahead)
            if project.fixed_ref:
                ui.info(ui.green, "*", ui.reset,
                        ui.blue, project.project.src.ljust(max_len), ui.reset,
                        ui.green, "fixed ref", project.fixed_ref,
                        ui.reset, ui.bold, ui.red,
                        numcommits)
            else:
                ui.info(ui.green, "*", ui.reset,
                        ui.blue, project.project.src.ljust(max_len), ui.reset,
                        ui.green, ":", project.current_branch,
                        "tracking",
                        ui.reset, ui.bold, ui.red,
                        numcommits, ui.green, project.tracking)
        else:
            if project.fixed_ref:
                ui.info(ui.green, "*", ui.reset,
                        ui.blue, project.project.src.ljust(max_len), ui.reset,
                        ui.green, "fixed ref", project.fixed_ref)
            else:
                ui.info(ui.green, "*", ui.reset,
                        ui.blue, project.project.src.ljust(max_len), ui.reset,
                        ui.green, ":", project.current_branch,
                        "tracking", project.tracking)
        if project.ahead_manifest or project.behind_manifest:
            numcommits = _print_behind_ahead(project.behind_manifest, project.ahead_manifest)
            ui.info(ui.bold, "Your branch", ui.green, project.current_branch,
                    ui.reset, ui.bold, "is", numcommits, "commits from branch",
                    ui.blue, project.manifest_branch)

    if not project.sync_and_clean:
        if project.status is not None:
            nlines = [x[:3] + project.project.src + "/" + x[3:]
                      for x in project.status]
            if nlines:
                print "\n".join(nlines)


def print_incorrect_projs(projects, max_len):
    """Print list of projets which are not on correct branch."""
    incorrect_projs = [x for x in projects if x.incorrect_proj]
    if incorrect_projs:
        ui.info()
        max_branch_len = max(len(x.current_branch) for x in incorrect_projs)
        max_branch_len = max(max_branch_len, len("Current"))
        ui.warning("Some projects are not on the expected branch")
        ui.info(ui.blue, " " * 2, "Project".ljust(max_len + 3), ui.reset,
                ui.green, "Current".ljust(max_branch_len + 3),
                "Manifest")
        for project in incorrect_projs:
            ui.info(ui.green, " *", ui.reset,
                    ui.blue, project.project.src.ljust(max_len + 3),
                    ui.green, project.current_branch.ljust(max_branch_len + 3),
                    ui.green, project.project.default_branch.name)


def print_not_on_a_branch(projects):
    """Print list of projects not on a branch."""
    not_on_a_branchs = [x for x in projects if x.not_on_a_branch]
    if not_on_a_branchs:
        ui.info()
        ui.warning("Some projects are not on any branch")
        for project in not_on_a_branchs:
            ui.info(ui.green, " *", ui.reset, ui.blue, project.project.src)
