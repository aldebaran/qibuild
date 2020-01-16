#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Add a build configuration. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.worktree
import qisys.parsers
from qisys import ui


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("name", type=ui.valid_filename)
    parser.add_argument("-t", "--toolchain", dest="toolchain")
    parser.add_argument("-p", "--profile", dest="profiles", action="append")
    parser.add_argument("--ide")
    parser.add_argument("-G", "--cmake-generator", dest="cmake_generator")
    parser.add_argument("--default", action="store_true")
    parser.add_argument("--host", action="store_true",
                        help="Wether this configuration is suitable to build host tools")
    parser.set_defaults(default=False, host=None)


def do(args):
    """ Main Entry Point """
    worktree = qisys.parsers.get_worktree(args, raises=False)
    name = args.name
    toolchain = args.toolchain
    profiles = args.profiles
    ide = args.ide
    cmake_generator = args.cmake_generator
    qibuild.config.add_build_config(name, toolchain=toolchain, profiles=profiles,
                                    ide=ide, cmake_generator=cmake_generator,
                                    host=args.host)
    if args.default:
        if worktree:
            build_worktree = qibuild.worktree.BuildWorkTree(worktree)
            build_worktree.set_default_config(name)
        else:
            raise Exception("Must be in a worktree to use --default")
