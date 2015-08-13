## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Push changes for review or to the server (deprecated)

"""
import sys

from qisys import ui
import qisys
import qisrc.git
import qisrc.parsers
import qisrc.maintainers
import qisrc.review

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser, positional=False)
    parser.add_argument("--no-review", action="store_false", dest="review",
        help="Do not go through code review")
    parser.add_argument("-n", "--dry-run", action="store_true", dest="dry_run",
        help="Dry run")
    parser.add_argument("--cc", "--reviewers", action="append", dest="reviewers",
        help="Add reviewers (full email or just username "
             "if the domain is the same as yours)")
    parser.add_argument("-t", "--topic", dest="topic",
        help="Add a topic to your code review. Useful for grouping patches together")
    parser.add_argument("-y", action="store_true", dest="yes",
        help="Push even if the project is not under code review. Default is to ask")
    parser.set_defaults(review=True, dry_run=False, yes=False)


def do(args):
    """ Main entry point """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_project = qisrc.parsers.get_one_git_project(git_worktree, args)
    git = qisrc.git.Git(git_project.path)
    current_branch = git.get_current_branch()
    if not current_branch:
        ui.error("Not currently on any branch")
        sys.exit(2)
    if git_project.review:
        maintainers = qisrc.maintainers.get(git_project, warn_if_none=True)
        reviewers = [x['email'] for x in maintainers]
        reviewers.extend(args.reviewers or list())
        # Prefer gerrit logins or groups instead of e-mails
        reviewers = [x.split("@")[0] for x in reviewers]
        qisrc.review.push(git_project, current_branch,
                            bypass_review=(not args.review),
                            dry_run=args.dry_run, reviewers=reviewers,
                            topic=args.topic)
    else:
        if args.dry_run:
            git.push("-n")
        else:
            if args.review and not args.yes:
                mess = """\
The project is not under code review.
Are you sure you want to run `git push` ?
This action cannot be undone\
"""
                answer = qisys.interact.ask_yes_no(mess, default=False)
                if answer:
                    git.push()
            else:
                git.push()
