## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List the relative paths of all projects in the worktree

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
    parser.set_defaults(names=True)

def do(args):
    """ Main method """
    worktree = qisys.parsers.get_worktree(args)
    projects = worktree.projects
    max_src  = max(len(x.src)  for x in projects)
    projects.sort(key=operator.attrgetter("src"))
    for project in projects:
        ui.info(ui.green, " * ", ui.blue, project.src)
