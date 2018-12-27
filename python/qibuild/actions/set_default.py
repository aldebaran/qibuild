#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Set the default build config for the given worktree. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qibuild.config


def configure_parser(parser):
    """ Configure parser for this action. """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("config")


def do(args):
    """ Main Entry Point. """
    config = args.config
    worktree = qisys.parsers.get_worktree(args)
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.set_default_config_for_worktree(worktree.root, config)
    qibuild_cfg.write()
