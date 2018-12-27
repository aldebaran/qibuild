#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" List translatable projects """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import operator

import qilinguist.parsers
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)


def do(args):
    """ Main entry point """
    linguist_worktree = qilinguist.parsers.get_linguist_worktree(args)
    projects = linguist_worktree.linguist_projects
    if not projects:
        return
    ui.info(ui.green, "Translatable projects in ",
            ui.reset, ui.blue, linguist_worktree.root)
    projects = sorted(projects, key=operator.attrgetter("name"))
    max_name = max(len(x.name) for x in projects)
    for project in projects:
        ui.info(ui.green, " * ",
                ui.blue, project.name.ljust(max_name + 2),
                ui.reset, "in",
                ui.bold, project.path)
