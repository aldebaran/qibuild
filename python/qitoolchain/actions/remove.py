## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Uninstall a toolchain

"""

import sys

from qibuild import ui
import qibuild
import qitoolchain


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("name",
        help="The name of the toolchain to remove")
    parser.add_argument('-f', "--force",
        dest="force_remove", action="store_true",
        help="""remove the whole toolchain, including any local packages you may
             have added to the toolchain.""")

def do(args):
    """ Main entry point  """
    tc_name  = args.name
    force_rm = args.force_remove
    if not tc_name in qitoolchain.get_tc_names():
        ui.warning("No such toolchain: %s" % tc_name)
        sys.exit(0)

    toolchain = qitoolchain.Toolchain(tc_name)
    ui.info(ui.green, "Removing toolchain", ui.blue, tc_name, ui.green, "...")
    toolchain.remove(force_remove=force_rm)
    ui.info(ui.green, "done")
