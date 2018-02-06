# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Display log between current branch and an other branch of the worktree """

import qisys.parsers
import qisrc.parsers
import qisrc.diff


def configure_parser(parser):
    qisys.parsers.project_parser(parser)
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("branch")
    parser.add_argument("--short", action="store_true")
    parser.set_defaults(short=False)


def do(args):
    branch = args.branch
    short = args.short
    if short:
        log_cmd = ["shortlog"]
    else:
        log_format = "%Cgreen%h%Creset -%C(yellow)%d%Creset %s %C(bold blue)<%an>%Creset"
        log_cmd = ["log", "--pretty=format:%s" % log_format]
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=False,
                                                  use_build_deps=True)
    qisrc.diff.diff_worktree(git_worktree, git_projects, branch, log_cmd)
