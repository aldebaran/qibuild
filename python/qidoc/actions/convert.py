#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Fix a qidoc2 worktree.
It will be usable both with qidoc2 and qidoc3 by default.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qidoc.convert


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    """ Main Entry Point """
    worktree = qisys.parsers.get_worktree(args)
    projects = qisys.parsers.get_projects(worktree, args)
    for project in projects:
        qidoc.convert.convert_project(project)
