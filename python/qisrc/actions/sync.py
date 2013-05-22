## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize the given worktree with its manifests

 * Clone any missing project
 * Configure projects for code review

"""

import sys

from qisys import ui
import qisys.parsers
import qisrc.git
import qisrc.sync
import qisrc.parsers
import qibuild.parsers


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)

    parser.add_argument("--no-review", dest="setup_review", action="store_false",
        help="Do not setup projects for review")
    parser.add_argument("--rebase-devel", action="store_true",
        help="Rebase devel branches. For advanced users only")
    parser.set_defaults(setup_review=True)

@ui.timer("Synchronizing worktree")
def do(args):
    """Main entry point"""
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_worktree.sync()
    # At this point we know that:
    #   - missing projects have been cloned
    #   - every repo that uses gerrit has been configured
    #   - every branch is configured correctly
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args, default_all=True)
    skipped = list()
    failed = list()
    ui.info(ui.green, ":: Syncing projects ...")
    for (i, git_project) in enumerate(git_projects):
        ui.info_count(i, len(git_projects),
                      ui.blue, git_project.src)

        (status, out) = git_project.sync(rebase_devel=args.rebase_devel)
        if status is None:
            ui.info(ui.brown, "  [skipped]")
            skipped.append((git_project.src, out))
        if status is False:
            ui.info(ui.red, "  [failed]")
            failed.append((git_project.src, out))
        if out:
            print ui.indent(out, num=2)

    if failed:
        print
        ui.error("Failed to sync some projects")
        display_errors(failed)

    if skipped:
        print
        ui.warning("Skipped some projects")
        display_errors(skipped)

    if failed:
        sys.exit(1)

def display_errors(errors):
    """ Helper function to display a summary at the end """
    for (src, err) in errors:
        ui.info(ui.blue, src)
        ui.info(ui.blue, "-" * len(src))
        ui.info(ui.indent(err, num=2))
