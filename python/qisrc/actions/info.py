#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Display info about the current git worktree """
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
    manifest = git_worktree.manifest
    ui.info(ui.green, "Manifest configured for",
            ui.reset, ui.bold, git_worktree.root, "\n",
            ui.reset, "url:   ", ui.bold, manifest.url, "\n",
            ui.reset, "branch:", ui.bold, manifest.branch)
    if manifest.groups:
        ui.info(ui.reset, "groups:", ui.bold, ", ".join(manifest.groups))
