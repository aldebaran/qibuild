#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Rebase repositories on top of an other branch of the manifest. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qisrc.parsers
import qisrc.rebase


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("--branch")
    parser.add_argument("--push", action="store_true",
                        help="Push the rebased branch")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Dry run")
    parser.add_argument("--force-run", action="store_false", dest="dry_run",
                        help="Use push --force. Use with caution.")
    parser.set_defaults(branch="master", push=False, dry_run=True)


def do(args):
    """ Main Entry Point """
    branch = args.branch
    push = args.push
    dry_run = args.dry_run
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=False,
                                                  use_build_deps=True)
    qisrc.rebase.rebase_worktree(git_worktree, git_projects, branch,
                                 push=push, dry_run=dry_run)
