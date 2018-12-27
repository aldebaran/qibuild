#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Output information about the given project. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.parsers
import qibuild.parsers
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name", nargs="?")


def do(args):
    """ Main entry point. """
    name = args.name
    build_worktree = qibuild.parsers.get_build_worktree(args, verbose=False)
    if name:
        build_project = build_worktree.get_build_project(name, raises=True)
    else:
        args.projects = list()
        build_project = qibuild.parsers.get_one_build_project(build_worktree, args)
    git_worktree = qisrc.parsers.get_git_worktree(args)
    git_project = qisys.parsers.find_parent_project(git_worktree.git_projects,
                                                    build_project.path)
    mess = "Build project: %s\n" % build_project.name
    mess += "src: %s\n" % build_project.src
    if git_project:
        mess += "repo: %s" % git_project.name
    ui.info(mess)
