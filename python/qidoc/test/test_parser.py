# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import qidoc.parsers


def test_get_french_doc_builder_(doc_worktree, args):
    doc_worktree.create_doc_project("world")
    args.language = "fr"
    args.projects = ["world"]
    builder = qidoc.parsers.get_doc_builder(args)
    assert builder.language == "fr"


def test_default_language_is_english(doc_worktree, args):
    doc_worktree.create_doc_project("world")
    args.projects = ["world"]
    builder = qidoc.parsers.get_doc_builder(args)
    assert builder.language == "en"
