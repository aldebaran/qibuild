## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Run a package found with qimvn find

"""

import sys

from qisys import ui
import qibuild.find
import qibuild.parsers
import qisys.parsers
import qisys.command
import qimvn.run

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    parser.add_argument("binary")
    parser.add_argument("bin_args", metavar="-- Binary arguments", nargs="*",
                        help="Binary arguments -- to escape the leading '-'")

def do(args):
    """Main entry point """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    return qimvn.run.run(build_worktree.build_projects, args.binary, args.bin_args)
