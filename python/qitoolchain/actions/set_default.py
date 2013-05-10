## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set a toolchain to use by default

"""

from qisys import ui
import qisys.parsers
import qibuild.parsers
import qitoolchain.parsers

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-c", "--config", metavar="NAME",
        help="Name of the toolchain", required=True)


def do(args):
    toolchain = qitoolchain.parsers.get_toolchain(args)
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_worktree.set_default_config(toolchain.name)
    ui.info("Now using toolchain", ui.blue, toolchain.name, ui.reset, "by default")
