#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qidoc.parsers


def test_get_french_doc_builder_(doc_worktree, args):
    """ Test Get Franch Doc Builder """
    doc_worktree.create_doc_project("world")
    args.language = "fr"
    args.projects = ["world"]
    builder = qidoc.parsers.get_doc_builder(args)
    assert builder.language == "fr"


def test_default_language_is_english(doc_worktree, args):
    """ Test Default Language Is English """
    doc_worktree.create_doc_project("world")
    args.projects = ["world"]
    builder = qidoc.parsers.get_doc_builder(args)
    assert builder.language == "en"
