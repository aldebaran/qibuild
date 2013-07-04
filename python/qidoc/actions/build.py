""" Build a doc project and its dependencies

"""

import operator

from qisys import ui
import qisys.parsers
import qidoc.parsers
import qidoc.builder

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    qidoc.parsers.build_doc_parser(parser)


def do(args):
    doc_builder = qidoc.parsers.get_doc_builder(args)
    doc_builder.configure()
    doc_builder.build()
