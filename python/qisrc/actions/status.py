#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""  List the state of all git repositories and exit """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qisrc.parsers
import qisrc.status
import qisrc.diff
import qisys
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    group = parser.add_argument_group("qisrc status options")
    group.add_argument("--untracked-files", "-u",
                       dest="untracked_files",
                       action="store_true",
                       help="display untracked files")
    group.add_argument("--short", "-S",
                       action="store_true",
                       help="do not display clean projects on expected branch")
    group.add_argument("--to", "-t",
                       dest="destination",
                       help="Make the difference between current manifest branch and a destination branch")


def do(args):
    """ Main method. """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=True,
                                                  use_build_deps=True)
    if not git_projects:
        qisrc.worktree.on_no_matching_projects(git_worktree, groups=args.groups)
        return
    num_projs = len(git_projects)
    max_len = max(len(p.src) for p in git_projects)
    state_projects = list()
    for (i, git_project) in enumerate(git_projects, start=1):
        if sys.stdout.isatty():
            src = git_project.src
            to_write = "Checking (%d/%d) " % (i, num_projs)
            to_write += src.ljust(max_len)
            sys.stdout.write(to_write + "\r")
            sys.stdout.flush()
        state_project = qisrc.status.check_state(git_project, args.untracked_files)
        state_projects.append(state_project)
    if sys.stdout.isatty():
        ui.info("Checking (%d/%d):" % (num_projs, num_projs), "done",
                " " * max_len)
    dirty = [x for x in state_projects if not x.sync_and_clean]
    ui.info("\n", ui.brown, "Dirty projects: ", len(dirty), "/", num_projs)
    projects_to_display = dirty if args.short else state_projects
    for git_project in projects_to_display:
        qisrc.status.print_state(git_project, max_len)
    max_len = max(max_len, len("Project"))
    qisrc.status.print_incorrect_projs(state_projects, max_len)
    qisrc.status.print_not_on_a_branch(state_projects)
    if not args.untracked_files:
        ui.info("Tips: use -u to show untracked files")
    if args.destination:
        mergeable = True
        ui.info("Check the difference between %s and %s" % (git_worktree.branch, args.destination))
        forked_projects = qisrc.diff.get_forked_projects(git_worktree, git_worktree.branch)
        for project in forked_projects:
            ui.info("\n", ui.white, " :: You worked on %s" % (project.name))
        for project in forked_projects:
            if not qisrc.diff.print_diff(project, git_worktree.branch, args.destination):
                mergeable = False
        if mergeable:
            ui.info("\n", ui.green, "Congratulation you can merge %s to %s" % (git_worktree.branch, args.destination))
            ui.info(ui.green, "To make a snapshot of this worktree state use: ", ui.blue, "'qisrc snapshot'")
        else:
            ui.info("\n", ui.red, "You need to rebase your projects before merging")
