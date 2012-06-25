## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Push changes for review

"""


import os
import sys
import qibuild.log
import qibuild
import qisrc

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("--no-review", action="store_false", dest="review",
        help="Do not go through code review")
    parser.add_argument("-n", "--dry-run", action="store_true", dest="dry_run",
        help="Dry run")
    parser.set_defaults(review=True, dry_run=False)


def do(args):
    """ Main entry point """
    git_path = qisrc.worktree.git_project_path_from_cwd()
    git = qisrc.git.Git(git_path)
    qisrc.review.push(git_path, git.get_current_branch(),
        review=args.review, dry_run=args.dry_run)

