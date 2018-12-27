#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" List the available groups """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisrc.parsers.worktree_parser(parser)


def do(args):
    """ Main Entry Point """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    local_groups = git_worktree.syncer.manifest.groups
    all_groups = list()
    groups_elem = qisrc.groups.get_root(git_worktree)
    if groups_elem is None:
        groups_elem = list()
    for group_elem in groups_elem:
        all_groups.append(group_elem.get("name"))
    for group in sorted(all_groups):
        if group in local_groups:
            ui.info("*", ui.green, group)
        else:
            ui.info(" ", group)
