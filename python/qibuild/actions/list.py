# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" List the name and path of every buildable project

"""

import re
import operator


from qisys import ui
import qisys.parsers
import qibuild.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("--names", action="store_true", dest="names",
                        help="sort by names")
    parser.add_argument("--paths", action="store_false", dest="names",
                        help="sort by path")
    parser.add_argument("pattern", metavar="PATTERN", nargs="?",
                        help="pattern to be matched")
    parser.set_defaults(names=True)


def do(args):
    """ Main method """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    projects = build_worktree.build_projects
    if not projects:
        on_empty_worktree(build_worktree)
        return
    ui.info(ui.green, "qibuild projects in:", ui.blue, build_worktree.root)
    max_name = max(len(x.name) for x in projects)
    max_src = max(len(x.src) for x in projects)
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


def on_empty_worktree(worktree):
    mess = """The worktree in {worktree.root}
does not contain any buildable project.

Please use:
    * `qisrc init` to fetch some sources
    * `qisrc create` to create a new qibuild project from scratch
    * `qibuild convert` to convert an exixting CMake project to
       a qibuild project
"""
    ui.warning(mess.format(worktree=worktree))
