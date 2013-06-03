""" Fix a qidoc2 worktree.

It will be usable both with qidoc2 and qidoc3 by default

"""

import qisys.parsers

import qidoc.convert

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    worktree = qisys.parsers.get_worktree(args)
    for project in worktree.projects:
        qidoc.convert.convert_project(project)
