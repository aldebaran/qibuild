## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Uninstall a toolchain

"""

import qibuild.log

import qibuild
import qitoolchain

LOGGER = qibuild.log.get_logger(__name__)

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
    toolchain = qitoolchain.Toolchain(tc_name)
    LOGGER.info("Removing toolchain %s", tc_name)
    toolchain.remove(force_remove=force_rm)
    LOGGER.info("Done removing toolchain %s", tc_name)
