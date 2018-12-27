#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Apply changes from a manifest xml path.
Useful to check everything is ok before pushing the manifest
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qisrc.parsers


def configure_parser(parser):
    """ Configure Parser """
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("xml_path")


def do(args):
    """ Main Entry Point """
    git_worktree = qisrc.parsers.get_git_worktree(args)
    ok = git_worktree.check_manifest(args.xml_path)
    if not ok:
        sys.exit(1)
