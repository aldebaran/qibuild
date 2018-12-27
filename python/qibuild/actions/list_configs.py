#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" List all the known configs. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import operator

import qibuild.worktree
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)


def do(args):
    """ Main Entry Point """
    worktree = qisys.parsers.get_worktree(args, raises=False)
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    configs = sorted(qibuild_cfg.configs.values(), key=operator.attrgetter("name"))
    ui.info("Known configs")
    for config in configs:
        ui.info("*", config)
    default_config = None
    if worktree:
        build_worktree = qibuild.worktree.BuildWorkTree(worktree)
        default_config = build_worktree.default_config
    if default_config:
        ui.info("Worktree in", build_worktree.root,
                "is using", default_config, "as a default config")
