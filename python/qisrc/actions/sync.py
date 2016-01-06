## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Synchronize the given worktree with its manifest

 * Clone any missing project
 * Configure projects for code review

"""

import sys

from qisys import ui
import qisys.parsers
import qisrc.git
import qisrc.sync
import qisrc.parsers
import qisys.parallel
import threading


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    qisys.parsers.parallel_parser(parser, default=1)

    group = parser.add_argument_group("qisrc sync options")
    group.add_argument("--rebase-devel", action="store_true",
                       help="Rebase development branches. Advanced users only")
    group.add_argument("--reset", action="store_true",
                       help="Do the same as `qisrc reset --all --force` after the fetch")

def print_overview(total, skipped, failed):
    out = [ ui.green, "Success:", ui.white, total - skipped - failed ]
    if skipped:
        out.append(ui.yellow)
    else:
        out.append(ui.blue)
    out.extend(("Skipped:", ui.white, skipped))
    if failed:
        out.append(ui.red)
    else:
        out.append(ui.blue)
    out.extend(("Failed:", ui.white, failed))
    ui.info(*out)

@ui.timer("Synchronizing worktree")
def do(args):
    """Main entry point"""
    reset = args.reset
    git_worktree = qisrc.parsers.get_git_worktree(args)
    sync_ok = git_worktree.sync()
    if not sync_ok:
        sys.exit(1)

    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=True,
                                                  use_build_deps=True)
    if not git_projects:
        qisrc.worktree.on_no_matching_projects(git_worktree, groups=args.groups)
        return
    git_worktree.configure_projects(git_projects)
    skipped = list()
    failed = list()
    ui.info(ui.green, ":: Syncing projects ...")
    max_src = max(len(x.src) for x in git_projects)

    # wrap with a list to sidestep problem described in
    # https://www.python.org/dev/peps/pep-3104/
    i = [0]
    lock = threading.Lock()

    def do_sync(git_project):
        if reset:
            (status, out) = git_project.reset()
        else:
            (status, out) = git_project.sync(rebase_devel=args.rebase_devel)

        with lock:
            ui.info_count(i[0], len(git_projects),
                          ui.blue, git_project.src.ljust(max_src))

            if status is None:
                ui.info(ui.brown, "  [skipped]")
                skipped.append((git_project.src, out))
            if status is False:
                ui.info(ui.red, "  [failed]")
                failed.append((git_project.src, out))
            if out:
                ui.info(ui.indent(out + "\n\n", num=2))

            i[0] += 1

    qisys.parallel.foreach(git_projects, do_sync, n_jobs=args.num_jobs)

    print_overview(len(git_projects), len(skipped), len(failed))
    if failed or skipped:
        sys.exit(1)
