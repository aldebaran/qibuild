#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Install a doc project and its depencies.
The index.html will be the one of the 'base project',
other projects will be put in relative to their 'dest'
attribute in the qiproject.xml.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qidoc.parsers
import qidoc.builder


def configure_parser(parser):
    """ Configure Parser """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    qidoc.parsers.build_doc_parser(parser)
    group = parser.add_argument_group("qidoc install options")
    group.add_argument("destdir")
    group.add_argument("--clean", action="store_true",
                       help="Clean destination first")


def do(args):
    """ Main Entry Point """
    doc_builder = qidoc.parsers.get_doc_builder(args)
    doc_builder.install(args.destdir, clean=args.clean)
