## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" List translatable projects

"""
import operator

from qisys import ui
import qisys.parsers
import qilinguist.parsers

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)


def do(args):
    """Main entry point"""
    linguist_worktree = qilinguist.parsers.get_linguist_worktree(args)
    projects = linguist_worktree.linguist_projects
    if not projects:
        return
    ui.info(ui.green, "Translatable projects in ",
            ui.reset, ui.blue, linguist_worktree.root)
    projects.sort(key=operator.attrgetter("name"))
    max_name = max(len(x.name) for x in projects)
    for project in projects:
        ui.info(ui.green, " * ",
                ui.blue, project.name.ljust(max_name + 2),
                ui.reset, "in",
                ui.bold, project.path)
