## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Install binary translations files

"""

import os

import qisys.parsers
import qilinguist.parsers

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("destination")


def do(args):
    """Main entry point"""
    destination = args.destination
    builder = qilinguist.parsers.get_linguist_builder(args)
    builder.install(destination)
