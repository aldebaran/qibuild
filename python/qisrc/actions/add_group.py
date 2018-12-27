#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Add a group to the current worktree """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys
import copy

import qisrc.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("group")


def do(args):
    """ Main Entry Point """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    group = args.group
    manifest = git_worktree.manifest
    if git_worktree.manifest.groups is None:
        groups = list()
    else:
        groups = copy.copy(git_worktree.manifest.groups)
    if group in groups:
        ui.error("Group", group, "already in use")
        sys.exit(1)
    else:
        groups.append(args.group)
    git_worktree.configure_manifest(manifest.url, groups=groups,
                                    branch=manifest.branch)
