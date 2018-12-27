#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Run a package found with qibuild find. """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qisys.command
import qisys.envsetter
import qibuild.run
import qibuild.find
import qibuild.parsers


def configure_parser(parser):
    """ Configure parser for this action. """
    qibuild.parsers.cmake_build_parser(parser)
    parser.add_argument("--no-exec", dest="exec_", action="store_false",
                        help="Do not use os.execve (Mostly useful for tests")
    parser.add_argument("binary")
    parser.add_argument("bin_args", metavar="-- Binary arguments", nargs="*",
                        help="Binary arguments -- to escape the leading '-'")


def do(args):
    """ Main entry point. """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    envsetter = qisys.envsetter.EnvSetter()
    envsetter.read_config(build_worktree.build_config.qibuild_cfg)
    qibuild.run.run(build_worktree.build_projects, args.binary, args.bin_args,
                    env=envsetter.get_build_env(), exec_=args.exec_)
