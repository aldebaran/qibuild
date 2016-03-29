## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Rebase repositories on top of an other branch of the manifest

"""

from qisys import ui
import qisys.parsers
import qisrc.parsers
import qisrc.rebase

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("--branch")
    parser.add_argument("--push", action="store_true",
                        help="Push the rebased branch. "
                             "Warning: uses --force, so be careful")
    parser.add_argument("--dry-run", action="store_true", dest="dry_run",
                        help="Dry run")
    parser.set_defaults(branch="master", push=False, dry_run=False)

def do(args):
    branch = args.branch
    push = args.push
    dry_run = args.dry_run

    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=False,
                                                  use_build_deps=True)

    qisrc.rebase.rebase_worktree(git_worktree, git_projects, branch,
                                 push=push, dry_run=dry_run)
