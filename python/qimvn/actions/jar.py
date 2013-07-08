#!/usr/bin/env python

## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Create a jar with files found in build directories.
"""

import qibuild.parsers
import qimvn.jar

from qisys import ui

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.build_parser(parser)
    parser.add_argument("jarname")
    parser.add_argument("files", nargs="*")

def do(args):
    """Main entry point """
    ui.debug("Creating jar '" + args.jarname + "'. Searching for", args.files)
    return qimvn.jar.jar(args.jarname, args.files, config=args.config)
