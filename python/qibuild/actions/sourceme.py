#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Generate and return the path to a suitable 'sourceme' file.
Useful when using a toolchain containing plugins.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.parsers


def configure_parser(parser):
    """ Configure Parser. """
    qibuild.parsers.cmake_build_parser(parser)


def do(args):
    """ Main Entry Point. """
    build_worktree = qibuild.parsers.get_build_worktree(args)
    sourceme = build_worktree.generate_sourceme()
    print(sourceme)
    return sourceme
