#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display log between current branch and an other branch of the worktree """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.diff
import qisrc.parsers
import qisys.parsers


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.project_parser(parser)
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("branch")
    parser.add_argument("--short", action="store_true")
    parser.set_defaults(short=False)


def do(args):
    """ Main Entry Point """
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
