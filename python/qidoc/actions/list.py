#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" List the qidoc projects """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import operator

import qidoc.parsers
import qidoc.convert
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    """ Main Entry Point """
    doc_worktree = qidoc.parsers.get_doc_worktree(args)
    doc_projects = doc_worktree.doc_projects
    if not doc_projects:
        return
    ui.info(ui.green, "qidoc projects in:", ui.blue, doc_worktree.root)
    max_name = max(len(x.name) for x in doc_projects)
    ui.info()
    for doc_type in ["doxygen", "sphinx"]:
        matching_projects = [x for x in doc_projects if x.doc_type == doc_type]
        matching_projects = sorted(matching_projects, key=operator.attrgetter("name"))
        if not matching_projects:
            continue
        ui.info(ui.green, doc_type.capitalize(),
                "projects")
        for project in matching_projects:
            ui.info(ui.green, " * ", ui.blue, project.name.ljust(max_name),
                    "  ", ui.reset, project.path)
        ui.info()
