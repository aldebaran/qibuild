## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Remove the given build config"""

from qisys import ui
import qisys.parsers
import qibuild.worktree

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name")

def do(args):
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
