#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Compile binary translations files """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qilinguist.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("--allow-untranslated-messages", action="store_false",
                        dest="raises")
    parser.set_defaults(raises=True)


def do(args):
    """ Main entry point """
    builder = qilinguist.parsers.get_linguist_builder(args)
    builder.build(raises=args.raises)
