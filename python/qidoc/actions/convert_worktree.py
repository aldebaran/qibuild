""" Fix a qidoc2 worktree so that it is usable both with
qidoc2 and qidoc3

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
