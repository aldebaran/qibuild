## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Display the toolchains names.

"""

from qisys import ui
import qisys.worktree
import qisys.parsers
import qitoolchain
import qibuild.parsers


def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    if not tc_names:
        ui.info("No toolchain yet", "\n",
                "Use `qitoolchain create` to create a new toolchain")
        return
    default_config = None
    try:
        build_worktree = qibuild.parsers.get_build_worktree(args)
        default_config = build_worktree.default_config
    except qisys.worktree.NotInWorkTree:
        pass
    ui.info("Known toolchains:")
    for tc_name in tc_names:
        if tc_name == default_config:
            ui.info("*", tc_name)
        else:
            ui.info(" ", tc_name)
    print
    if default_config is not None:
        ui.info("WorkTree", ui.green, build_worktree.root, ui.reset, "is using",
                ui.blue, default_config, ui.reset,
                "as its default toolchain.")
    ui.info("Use ``qitoolchain info <tc_name>`` for more info")
