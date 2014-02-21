## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Uninstall a toolchain

"""

from qisys import ui
import qisys.parsers
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name",
        help="The name of the toolchain to remove")
    parser.add_argument('-f', "--force",
        dest="force_remove", action="store_true",
        help="""remove the whole toolchain, including any local packages you may
             have added to the toolchain.""")

def do(args):
    """ Main entry point  """
    force_rm = args.force_remove
    tc = qitoolchain.get_toolchain(args.name)
    ui.info(ui.green, "Removing toolchain", ui.blue, tc.name)
    tc.remove(force_remove=force_rm)
    ui.info(ui.green, "done")
