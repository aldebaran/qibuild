#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Build a doc project and its dependencies """
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


def do(args):
    """ Main Entry Point """
    doc_builder = qidoc.parsers.get_doc_builder(args)
    doc_builder.configure()
    doc_builder.build(pdb=args.pdb)
