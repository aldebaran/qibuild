# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Fix a qidoc2 worktree.

It will be usable both with qidoc2 and qidoc3 by default

"""

import qisys.parsers

import qidoc.convert


def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    worktree = qisys.parsers.get_worktree(args)
    projects = qisys.parsers.get_projects(worktree, args)
    for project in projects:
        qidoc.convert.convert_project(project)
