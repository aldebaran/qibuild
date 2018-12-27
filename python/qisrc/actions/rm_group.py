#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Remove a group from the current worktree """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys
import copy

from qisys import ui
import qisrc.parsers


def configure_parser(parser):
    """ Configure Parser """
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("group")


def do(args):
    """ MAin Entry Point """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    group = args.group
    manifest = git_worktree.manifest
    groups = copy.copy(git_worktree.manifest.groups)
    if group in groups:
        groups.remove(args.group)
    else:
        ui.info("No such group:", group)
        sys.exit(0)
    git_worktree.configure_manifest(manifest.url, groups=groups,
                                    branch=manifest.branch)
