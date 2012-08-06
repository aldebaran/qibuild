## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the name and path of every buildable project

"""

import os


from qibuild import ui
import qibuild


def configure_parser(parser):
    """ Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("-n", action="store_true", dest="names",
                        help="sort by names")
    parser.add_argument("-p", action="store_false", dest="names",
                        help="sort by path")
    parser.set_defaults(names=True)


def do(args):
    """ Main method """
    toc = qibuild.toc.toc_open(args.worktree, args)
    ui.info(ui.green, "qibuild projects in:", ui.blue, toc.worktree.root)
    projects = toc.projects[:]
    for project in projects:
        project.directory = os.path.relpath(project.directory, toc.worktree.root)
    max_name = max([len(x.name)      for x in projects])
    max_src  = max([len(x.directory) for x in projects])
    if args.names:
        for project in projects:
            ui.info(ui.green, " * ", ui.blue, project.name.ljust(max_name + 2), ui.reset, project.directory)
    else:
        for project in projects:
            ui.info(ui.green, " * ", ui.blue, project.directory.ljust(max_src + 2), ui.reset, project.name)
