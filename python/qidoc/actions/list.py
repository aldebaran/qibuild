## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""List the doc projects of the given worktree."""

import qibuild
import qidoc.core
import qisrc.cmdparse

from qibuild import ui

def configure_parser(parser):
    """Configure parser for this action."""
    qibuild.parsers.worktree_parser(parser)
    qibuild.parsers.project_parser(parser)

def do(args):
    """Main entry point"""
    projects = qisrc.cmdparse.projects_from_args(args)
    builder = qidoc.core.QiDocBuilder(projects, args.worktree)

    ui.info("List of qidoc projects in", builder.worktree.root, end='\n\n')
    for doc_type, docs in builder.documentations_list():
        ui.info(doc_type.title(), 'documentation:')
        for doc in docs:
            ui.info(' -', doc.name)
        ui.info('')
