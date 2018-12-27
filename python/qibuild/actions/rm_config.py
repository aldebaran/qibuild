#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Remove the given build config. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qibuild.worktree


def configure_parser(parser):
    """ Configure Parser. """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name")


def do(args):
    """ Main Entry Point. """
    name = args.name
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    del qibuild_cfg.configs[name]
    # Also remove default config from global qibuild.xml file, so
    # that we don't get a default config pointing to a non-existing
    # config
    for worktree in qibuild_cfg.worktrees.values():
        if worktree.defaults.config == name:
            qibuild_cfg.set_default_config_for_worktree(worktree.path, None)
    qibuild_cfg.write()
