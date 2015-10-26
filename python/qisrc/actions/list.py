## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the names and paths of every project, or those matching a pattern

"""

import re
import operator

from qisys import ui
import qisys.parsers
import qisrc.parsers
import qisrc.worktree


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("--names", action="store_true", dest="names",
                        help="sort by names")
    parser.add_argument("--paths", action="store_false", dest="names",
                        help="sort by path")
    parser.add_argument("pattern", metavar="PATTERN", nargs="?",
                        help="pattern to be matched")
    qisrc.parsers.groups_parser(parser)
    parser.set_defaults(names=True)

def do(args):
    """ Main method """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    if not git_worktree.git_projects:
        qisrc.worktree.on_no_matching_projects(git_worktree)
        return
    ui.info(ui.green, "qisrc projects in:", ui.blue, git_worktree.root)
    if args.groups:
        projects = git_worktree.get_git_projects(groups=args.groups)
    else:
        projects = git_worktree.git_projects
    max_name = max(len(x.name) for x in projects)
    max_src  = max(len(x.src)  for x in projects)
    regex = args.pattern
    if args.pattern:
        regex = re.compile(regex)
    if args.names:
        projects.sort(key=operator.attrgetter("name"))
    else:
        projects.sort(key=operator.attrgetter("src"))
    for project in projects:
        if args.names:
            items = (project.name.ljust(max_name + 2), project.path)
        else:
            items = (project.src.ljust(max_src + 2), project.name)
        if not regex or regex.search(items[0]) or regex.search(items[1]):
            ui.info(ui.green, " * ", ui.blue, items[0], ui.reset, items[1])
