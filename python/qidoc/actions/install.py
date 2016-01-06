## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Install a doc project and its depencies.

The index.html will be the one of the 'base project',
other projects will be put in relative to their 'dest'
attribute in the qiproject.xml

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
    group = parser.add_argument_group("qidoc install options")
    group.add_argument("destdir")
    group.add_argument("--clean", action="store_true",
                       help="Clean destination first")


def do(args):
    doc_builder = qidoc.parsers.get_doc_builder(args)
    doc_builder.install(args.destdir, clean=args.clean)
