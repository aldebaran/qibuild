## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Uninstall a toolchain

"""

from qisys import ui
import qisys.parsers
import qibuild.config
import qitoolchain

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name",
        help="The name of the toolchain to remove")
    parser.add_argument('-f', "--force",
        dest="force", action="store_true",
        help="""remove the whole toolchain, including any local packages you may
             have added to the toolchain.""")

def do(args):
    """ Main entry point  """
    tc = qitoolchain.get_toolchain(args.name)
    if args.force:
        ui.info(ui.green, "Removing toolchain", ui.blue, tc.name)
        tc.remove()
        ui.info(ui.green, "done")
    else:
        ui.info("Would remove toolchain", ui.blue, tc.name)
        return
    # Also remove default config from global qibuild.xml file, so
    # that we don't get a default config pointing to a non-existing
    # toolchain
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    for worktree in qibuild_cfg.worktrees.values():
        if worktree.defaults.config == args.name:
            qibuild_cfg.set_default_config_for_worktree(worktree.path, None)
    qibuild_cfg.write()
