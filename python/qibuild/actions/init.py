#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Initialize a new qibuild worktree. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import argparse

import qibuild.parsers
import qibuild.worktree
import qisys.worktree
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.worktree_parser(parser)
    # backward-compat:
    parser.add_argument("-c", "--config", help=argparse.SUPPRESS)
    parser.add_argument("--interactive", action="store_true",
                        help=argparse.SUPPRESS)
    parser.set_defaults(interactive=False)


def do(args):
    """ Main entry point. """
    root = args.worktree or os.getcwd()
    if os.path.exists(os.path.join(root, '.qi')):
        raise Exception("A .qi directory already exists here. " +
                        "Please remove it or initialize elsewhere.")
    worktree = qisys.worktree.WorkTree(root)
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    if args.config:
        ui.warning("`qibuild init -c` is deprecated", "\n",
                   "Use `qitoolchain set-default` instead")
        qisys.script.run_action("qitoolchain.actions.set_default",
                                [args.config, "--worktree", build_worktree.root])
    if args.interactive:
        ui.warning("`qibuild init --interactive` is deprecated", "\n",
                   "Use `qibuild config --wizard` instead")
        qisys.script.run_action("qibuild.actions.config",
                                ["--wizard", "--worktree", build_worktree.root])
