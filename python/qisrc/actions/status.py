## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the state of all git repositories and exit
"""

import os
import sys

from qisys import ui
import qisys
import qisrc


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

def stat_tracking_remote(git, branch, tracking):
    behind = 0
    ahead = 0
    (ret, out) = git.call("rev-list", "--left-right", "%s..%s" % (tracking, branch), raises=False)
    if ret == 0:
        ahead = len(out.split())
    (ret, out) = git.call("rev-list", "--left-right", "%s..%s" % (branch, tracking), raises=False)
    if ret == 0:
        behind = len(out.split())
    return (ahead, behind)

def do(args):
    """ Main method """
    qiwt = qisys.worktree.open_worktree(args.worktree)
    gitrepo = list()
    dirty = list()
    incorrect = list()

    git_projects = qiwt.git_projects
    manifests = qiwt.get_manifest_projects()
    git_projects = list(set(git_projects) - set(manifests))

    num_projs = len(git_projects)
    max_len = max([len(p.src) for p in git_projects])
    i = 1
    incorrect_projs = list()
    not_on_a_branch = list()
    for git_project in git_projects:
        git = qisrc.git.open(git_project.path)
        if sys.stdout.isatty():
            src = git_project.src
            to_write = "Checking (%d/%d) " % (i, num_projs)
            to_write += src.ljust(max_len)
            sys.stdout.write(to_write + "\r")
            sys.stdout.flush()
            if i == num_projs:
                ui.info("Checking (%d/%d):" % (num_projs, num_projs), "done",
                        " " * max_len)
        i = i + 1
        if git.is_valid():
            clean = git.is_clean(untracked=args.untracked_files)

            #clean worktree, but is the current branch sync with the remote one?
            if clean:
                branch = git.get_current_branch()
                if branch is None:
                    not_on_a_branch.append(git_project.src)
                    continue
                if branch != git_project.branch:
                    incorrect_projs.append((git_project.src, branch, git_project.branch))
                    incorrect.append(git_project)
                tracking = git.get_tracking_branch()
                (ahead, behind) = stat_tracking_remote(git, branch, tracking)
                if ahead != 0 or behind != 0:
                    clean = False

            if args.show_branch or not clean:
                gitrepo.append(git_project)
            if not clean:
                dirty.append(git_project)

    ui.info("\n", ui.brown, "Dirty projects", len(dirty), "/", len(git_projects))

    for git_project in gitrepo:
        git = qisrc.git.open(git_project.path)
        shortpath = os.path.relpath(git_project.path, qiwt.root)
        if git.is_valid():
            branch = git.get_current_branch()
            tracking = git.get_tracking_branch()
            (ahead, behind) = stat_tracking_remote(git, branch, tracking)
            ui.info(ui.green, "*", ui.reset,
                    ui.blue, shortpath.ljust(max_len), ui.reset,
                    ui.green, ":", branch, "tracking", tracking)
            if ahead:
                ui.info(ui.bold, "Your branch is", ahead, ui.reset, "commits ahead")
            if behind:
                ui.info(ui.bold, "Your branch is", behind, ui.reset, "commits behind")

        if not git.is_clean(untracked=args.untracked_files):
            if args.untracked_files:
                (status_, out) = git.call("status", "-s", raises=False)
            else:
                (status_, out) = git.call("status", "-suno", raises=False)
            nlines = [ x[:3] + shortpath + "/" + x[3:] for x in out.splitlines() if len(x.strip()) > 0 ]
            print "\n".join(nlines)

    max_len = max([max_len, len("Project")])
    if incorrect_projs:
        ui.info()
        max_branch_len = max([len(x[1]) for x in incorrect_projs])
        max_branch_len = max([max_branch_len, len("Current")])
        ui.warning("Some projects are not on the expected branch")
        ui.info(ui.blue, " " *2, "Project".ljust(max_len + 3), ui.reset,
                ui.green, "Current".ljust(max_branch_len + 3),
                "Manifest")
        for (project, local_branch, manifest_branch) in incorrect_projs:
            ui.info(ui.green, " *", ui.reset,
                    ui.blue, project.ljust(max_len + 3),
                    ui.green, local_branch.ljust(max_branch_len + 3),
                    ui.green, manifest_branch)

    if not_on_a_branch:
        ui.info()
        ui.warning("Som projects are not on any branch")
        for project in not_on_a_branch:
            ui.info(ui.green, " *", ui.reset, ui.blue, project)

    if not args.untracked_files:
        ui.info("Tips: use -u to show untracked files")

