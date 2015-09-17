## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Build a doc project and its dependencies

"""

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
    doc_builder.build(pdb=args.pdb)
