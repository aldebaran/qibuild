#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Update translations sources from source code """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.parsers
import qilinguist.parsers


def configure_parser(parser):
    """ Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)


def do(args):
    """ Main entry point """
    builder = qilinguist.parsers.get_linguist_builder(args)
    builder.configure()
