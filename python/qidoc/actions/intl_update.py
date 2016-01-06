## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Update message catalogs for the given doc project

(currently only available for sphinx projects)
Requires sphinx-intl

"""

import qisys.parsers
import qidoc.parsers

def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    qidoc.parsers.build_doc_parser(parser)

def do(args):
    """ Main entry point """
    doc_builder = qidoc.parsers.get_doc_builder(args)
    doc_builder.configure()
    doc_builder.intl_update()
