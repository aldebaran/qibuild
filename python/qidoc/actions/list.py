## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""List the doc projects of the given worktree."""

import os

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

    ui.info(ui.blue, "List of qidoc projects in", ui.red,
            builder.worktree.root, end='')
    if builder.is_in_project():
        if len(projects) == 1:
            ui.info(ui.blue, '[ project:', ui.green, projects[0].src, ui.blue,
                    ']', end='')
        else:
            ui.info(ui.blue, '[ several projects in current directory ]', end='')
    ui.info('', end='\n\n')
    for doc_type, docs in builder.documentations_list():
        ui.info(ui.blue, doc_type.title(), 'documentation:')
        for doc in docs:
            ui.info(ui.green, '  *', ui.blue, doc.name.ljust(25), ui.red,
                    os.path.relpath(doc.src, builder.worktree.root))
        ui.info('')
