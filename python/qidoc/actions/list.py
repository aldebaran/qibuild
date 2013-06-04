""" List the qidoc projects

"""

from qisys import ui
import qisys.parsers
import qidoc.parsers

import qidoc.convert

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    doc_worktree = qidoc.parsers.get_doc_worktree(args)
    for doc_project in doc_worktree.doc_projects:
        print doc_project.src
