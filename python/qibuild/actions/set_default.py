## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set the default build config for the given worktree """

import qisys.parsers
import qibuild.config

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("config")

def do(args):
    config = args.config
    worktree = qisys.parsers.get_worktree(args)
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.set_default_config_for_worktree(worktree.root, config)
    qibuild_cfg.write()
