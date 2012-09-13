## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""List the doc projects of the given worktree."""

import operator
import os

import qibuild
import qidoc.core

from qibuild import ui

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.worktree_parser(parser)

def do(args):
    """Main entry point"""
    builder = qidoc.core.QiDocBuilder(args.worktree)

    ui.info("List of qidoc projects in", builder.worktree.root, end='\n\n')
    for doc_type, docs in builder.documentations_list():
        ui.info(doc_type.title(), 'documentation:')
        for doc in docs:
            ui.info(' -', doc.name)
        ui.info('')
