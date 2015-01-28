## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Run git grep on every project

Options are the same as in git grep, e.g.:

  qisrc grep -- -niC2 foo

"""

import os
import sys

from qisys import ui
import qisrc.git
import qisrc.parsers
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action."""
    qisrc.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser, positional=False)
    parser.add_argument("--path", help="type of patch to print",
            default="project", choices=['none', 'absolute', 'worktree', 'project'])
    parser.add_argument("git_grep_opts", metavar="-- git grep options", nargs="+",
                        help="git grep options preceded with -- to escape the leading '-'")

def do(args):
    """Main entry point."""
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_projects = qisrc.parsers.get_git_projects(git_worktree, args, default_all=True,
                                                  use_build_deps=args.use_deps)
    git_grep_opts = args.git_grep_opts
    if args.path == 'none':
        git_grep_opts.insert(0, "-h")
    else:
        git_grep_opts.insert(0, "-H")
        if args.path == 'absolute' or args.path == 'worktree':
            git_grep_opts.insert(0, "-I")
            git_grep_opts.insert(0, "--null")
    if ui.config_color(sys.stdout):
        git_grep_opts.insert(0, "--color=always")

    if not git_projects:
        qisrc.worktree.on_no_matching_projects(git_worktree, groups=args.groups)
        sys.exit(0)

    max_src = max(len(x.src) for x in git_projects)
    retcode = 1
    for i, project in enumerate(git_projects):
        ui.info_count(i, len(git_projects),
                      ui.green, "Looking in",
                      ui.blue, project.src.ljust(max_src),
                      end="\r")
        git = qisrc.git.Git(project.path)
        (status, out) = git.call("grep", *git_grep_opts, raises=False)
        if out != "":
            if args.path == 'absolute' or args.path == 'worktree':
                lines = out.splitlines()
                out_lines = list()
                for line in lines:
                    line_split = line.split('\0')
                    prepend = project.src if args.path == 'worktree' else project.path
                    line_split[0] = os.path.join(prepend, line_split[0])
                    out_lines.append(":".join(line_split))
                out = '\n'.join(out_lines)
            ui.info("\n", ui.reset, out)
        if status == 0:
            retcode = 0
    if not out:
        ui.info(ui.reset)
    sys.exit(retcode)
