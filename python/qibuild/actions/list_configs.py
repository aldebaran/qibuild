# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

"""List all the known configs """

import operator

from qisys import ui
import qisys.parsers
import qibuild.worktree


def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)


def do(args):
    worktree = qisys.parsers.get_worktree(args, raises=False)

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    configs = qibuild_cfg.configs.values()
    configs.sort(key=operator.attrgetter("name"))
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
