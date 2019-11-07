#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import pytest

import qilinguist.parsers
import qilinguist.qigettext
import qilinguist.pml_translator


def test_parsing_pml_from_wortktree(worktree, args):
    """ Test Parsing Pml From Worktree """
    _foo_proj = worktree.create_project("foo")
    worktree.tmpdir.join("foo", "foo.pml").write('<Package name="foo" />')
    args.projects = ["foo/foo.pml"]
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 1
    project = projects[0]
    assert isinstance(project, qilinguist.pml_translator.PMLTranslator)


def test_parsing_pml_no_worktree(cd_to_tmpdir, tmpdir, args):
    """ Test Parsing Pml No Worktree """
    pml_path = tmpdir.join("foo.pml")
    pml_path.write('<Package name="foo" />')
    args.projects = [pml_path.strpath]
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 1
    project = projects[0]
    assert isinstance(project, qilinguist.pml_translator.PMLTranslator)


def test_names_no_worktree(cd_to_tmpdir, args):
    """ Test Names No Worktree """
    args.projects = ["foo"]
    with pytest.raises(Exception) as e:
        qilinguist.parsers.get_linguist_projects(args)
    assert str(e) == "Cannot use project names when running outside a worktree"


def test_no_worktree_no_args(cd_to_tmpdir, args):
    """ Test No Worktree No Args """
    args.projects = list()
    with pytest.raises(Exception) as e:
        qilinguist.parsers.get_linguist_projects(args)
    assert str(e) == "You should specify at least a pml path when running outside a worktree"


def test_names_and_pml_from_worktree(linguist_worktree, args, monkeypatch):
    """ Test Names And Pml From Worktree """
    linguist_worktree.create_gettext_project("foo")
    linguist_worktree.tmpdir.join("bar.pml").write("""\n<Package name="bar" />\n""")
    args.projects = ["bar.pml", "foo"]
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 2
    foo1 = projects[0]
    assert foo1.name == "foo"
    assert foo1.linguas == ["fr_FR", "en_US"]
    bar1 = projects[1]
    assert bar1.pml_path == linguist_worktree.tmpdir.join("bar.pml").strpath


def test_no_args_in_project(linguist_worktree, monkeypatch, args):
    """ Test No Args In Project """
    foo_proj = linguist_worktree.create_gettext_project("foo")
    monkeypatch.chdir(foo_proj.path)
    args.projects = list()
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 1
    assert projects[0].name == "foo"
