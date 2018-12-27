#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qidoc.test.conftest import TestDocWorkTree


def test_create_projects(cd_to_tmpdir):
    """ Test Create Projects """
    doc_worktree = TestDocWorkTree()
    doc_worktree.add_templates()
    doc_worktree.create_doxygen_project("foo")
    doc_worktree.create_sphinx_project("bar", depends=["foo"])
    foo_proj = doc_worktree.get_doc_project("foo")
    bar_proj = doc_worktree.get_doc_project("bar")
    assert foo_proj.doc_type == "doxygen"
    assert foo_proj.depends == list()
    assert foo_proj.name == "foo"
    assert bar_proj.name == "bar"
    assert bar_proj.doc_type == "sphinx"
    assert bar_proj.depends == ["foo"]
    assert doc_worktree.template_project.src == "templates"
