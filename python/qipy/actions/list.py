""" List all known python projects """

from qisys import ui

import qisys.parsers
import qipy.parsers
import qibuild.parsers

def configure_parser(parser):
    qibuild.parsers.cmake_build_parser(parser)

def do(args):
    python_worktree = qipy.parsers.get_python_worktree(args)
    python_projects = python_worktree.python_projects
    if not python_projects:
        return
    ui.info(ui.green, "python projects in:", ui.blue, python_worktree.root)
    for project in python_projects:
        ui.info(ui.green, " * ", ui.blue, project.name)
