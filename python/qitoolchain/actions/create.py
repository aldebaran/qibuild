#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Configure a worktree to use a toolchain.
Toolchain packages and known configurations will be fetched from an URL.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import sys

import qitoolchain
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name", metavar="NAME",
                        help="Name of the toolchain", type=ui.valid_filename)
    parser.add_argument("--feed-name", "--name", dest="feed_name",
                        help="Name of the feed. To be specified when using a git url")
    parser.add_argument("-b", "--branch",
                        help="Branch of the git url to use")
    parser.add_argument("feed", metavar="TOOLCHAIN_FEED",
                        help="Optional: path to the toolchain configuration file.\n"
                        "If not given, the toolchain will be empty.\n"
                        "May be a local file, a url or a git URL (in this case\n"
                        "--feed-name must be used)",
                        nargs="?")
    parser.set_defaults(branch="master")


def do(args):
    """ Main entry point """
    if "--name" in sys.argv:
        ui.warning("--name is deprecated, use --feed-name instead")
    feed = args.feed
    # Normalize feed path:
    if feed and os.path.exists(feed):
        feed = qisys.sh.to_native_path(feed)
    tc_name = args.name
    qitoolchain.ensure_name_is_valid(tc_name)
    if tc_name in qitoolchain.get_tc_names():
        toolchain = qitoolchain.Toolchain(tc_name)
        ui.info(tc_name, "already exists,", "updating without removing")
    toolchain = qitoolchain.Toolchain(tc_name)
    if feed:
        toolchain.update(feed, branch=args.branch, name=args.feed_name)
    return toolchain
