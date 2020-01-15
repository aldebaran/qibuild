#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

from qidoc.test.conftest import TestDocWorkTree


def test_qidoc2_happy(qidoc_action):
    """ Test QiDoc 2 Happy """
    qidoc_action.add_test_project("qidoc2/templates")
    qidoc_action.add_test_project("qidoc2/happy")
    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 4
    assert doc_projects[0].name == "a_doxy"
    assert doc_projects[0].dest == "ref/a"
    assert doc_projects[1].name == "b_doxy"
    assert doc_projects[1].depends == ["a_doxy"]
    assert doc_projects[2].name == "c_sphinx"
    assert doc_projects[2].depends == ["b_doxy"]
    tmpl_proj = doc_worktree.template_project
    assert tmpl_proj.src == "qidoc2/templates"


def test_read_deps(doc_worktree):
    """ Test Read Deps """
    _world_proj = doc_worktree.add_test_project("world")
    hello_proj = doc_worktree.add_test_project("hello")
    assert hello_proj.depends == ["world"]


def test_prebuild(doc_worktree):
    """ Test PreBuild """
    prebuild_proj = doc_worktree.add_test_project("prebuild")
    assert prebuild_proj.name == "prebuild"
    assert prebuild_proj.prebuild_script == "tools/gen_rst.py"


def test_examples(doc_worktree):
    """ Test Exemples """
    examples_proj = doc_worktree.add_test_project("examples")
    assert examples_proj.name == "examples"
    assert examples_proj.examples == [
        "samples/a",
        "samples/b"]
