#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Remove a project from a worktree """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys
import qisys.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("src", metavar="PATH",
                        help="Path to the project sources")
    parser.add_argument("--from-disk", dest="from_disk", action="store_true",
                        help="Also remove project sources from disk")
    parser.set_defaults(from_disk=False)


def do(args):
    """ Main entry point """
    src = args.src
    path = qisys.sh.to_native_path(src)
    worktree = qisys.parsers.get_worktree(args)
    worktree.remove_project(path, from_disk=args.from_disk)
