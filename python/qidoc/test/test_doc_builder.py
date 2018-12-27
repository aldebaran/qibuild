#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import mock

from qidoc.builder import DocBuilder


def test_doc_builder_solve_deps_by_default(doc_worktree):
    """ Test Doc Builder Solved Deps By Default """
    qibuild_doc = doc_worktree.create_sphinx_project("qibuild")
    general_doc = doc_worktree.create_sphinx_project("general", depends=["qibuild"])
    doc_builder = DocBuilder(doc_worktree, "general")
    assert doc_builder.get_dep_projects() == [qibuild_doc, general_doc]


def test_using_dash_s(doc_worktree):
    """ Test Using Dash s """
    _qibuild_doc = doc_worktree.create_sphinx_project("qibuild")
    general_doc = doc_worktree.create_sphinx_project("general", depends=["qibuild"])
    doc_builder = DocBuilder(doc_worktree, "general")
    doc_builder.single = True
    assert doc_builder.get_dep_projects() == [general_doc]


def test_base_project_install(doc_worktree, tmpdir):
    """ Test Base Project Install """
    doc_worktree.add_test_project("world")
    doc_worktree.add_test_project("hello")
    doc_builder = DocBuilder(doc_worktree, "hello")
    hello_inst = tmpdir.join("inst", "hello")
    doc_builder.install(hello_inst.strpath)
    hello_index = hello_inst.join("index.html")
    assert "hello" in hello_index.read().decode("utf-8")
    world_index = hello_inst.join("ref/world/index.html")
    assert "world" in world_index.read().decode("utf-8")


def test_install_doxy(doc_worktree, tmpdir):
    """ Test Install Doxy """
    doc_worktree.add_test_project("libqi/doc/doxygen")
    doc_builder = DocBuilder(doc_worktree, "qi-api")
    inst_dir = tmpdir.join("inst")
    doc_builder.configure()
    doc_builder.build()
    doc_builder.install(inst_dir.strpath)
    assert "qi" in inst_dir.join("index.html").read()


def test_setting_base_project_resets_dests(doc_worktree):
    """ Test Setting Base Project Reset Dests """
    doc_worktree.add_test_project("world")
    doc_worktree.add_test_project("hello")
    _doc_builder = DocBuilder(doc_worktree, "hello")
    hello_proj = doc_worktree.get_doc_project("hello")
    world_proj = doc_worktree.get_doc_project("world")
    assert hello_proj.dest == "."
    assert world_proj.dest == "ref/world"
    _doc_builder = DocBuilder(doc_worktree, "world")
    world_proj = doc_worktree.get_doc_project("world")
    assert world_proj.dest == "."


def test_setting_language(doc_worktree):
    """ Test Setting Language """
    _translateme_proj = doc_worktree.add_test_project("translateme")
    doc_builder = DocBuilder(doc_worktree, "translateme")
    doc_builder.language = "fr"
    doc_builder.configure()
    with mock.patch("sphinx.main") as mock_sphinx:
        mock_sphinx.return_value = 0
        doc_builder.build()
        args_list = mock_sphinx.call_args_list
        assert len(args_list) == 1
        last_call = args_list[0]
        argv = last_call[1]["argv"]
        assert "-Dlanguage=fr" in argv
