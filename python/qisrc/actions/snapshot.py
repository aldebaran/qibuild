#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Generate a snapshot of all the git projects """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisrc.git
import qisrc.parsers
import qisrc.snapshot
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.worktree_parser(parser)
    group = parser.add_argument_group("qisrc snapshot options")
    group.add_argument("snapshot_path", nargs="?",
                       help="Path to the output snapshot file. " +
                       "Use `qisrc reset --force --snapshot snapshot_path` to load a snapshot")
    group.add_argument("--deprecated-format", action="store_true",
                       help="Only used for retro-compatibility")
    parser.set_defaults(deprecated_format=False)


def do(args):
    """ Main entry point. """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    ui.info(ui.green, "Current worktree:", ui.reset, ui.bold, git_worktree.root)
    snapshot_path = args.snapshot_path
    if not snapshot_path:
        snapshot_path = os.path.join(os.getcwd(), "snapshot.json")
    qisrc.snapshot.generate_snapshot(git_worktree, snapshot_path,
                                     deprecated_format=args.deprecated_format)
    return snapshot_path
