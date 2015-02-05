## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
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
    qisys.parsers.default_parser(parser)


def do(args):
    """ Main method """
    tc_names = qitoolchain.get_tc_names()
    if not tc_names:
        ui.info("No toolchain yet", "\n",
                "Use `qitoolchain create` to create a new toolchain")
        return
    ui.info("Known toolchains:")
    for tc_name in tc_names:
        ui.info("*", tc_name)
    ui.info("Use ``qitoolchain info <tc_name>`` for more info")
