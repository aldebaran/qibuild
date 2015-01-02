## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qilinguist.parsers
import qilinguist.pml_translator
import qilinguist.qigettext

import pytest

def test_parsing_pml_from_wortktree(worktree, args):
    foo_proj = worktree.create_project("foo")
    worktree.tmpdir.join("foo", "foo.pml").write('<Package name="foo" />')
    args.projects = ["foo/foo.pml"]
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 1
    project = projects[0]
    assert isinstance(project, qilinguist.pml_translator.PMLTranslator)

def test_parsing_pml_no_worktree(cd_to_tmpdir, tmpdir, args):
    pml_path = tmpdir.join("foo.pml")
    pml_path.write('<Package name="foo" />')
    args.projects = [pml_path.strpath]
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 1
    project = projects[0]
    assert isinstance(project, qilinguist.pml_translator.PMLTranslator)

def test_names_no_worktree(cd_to_tmpdir, args):
    args.projects = ["foo"]
    with pytest.raises(Exception) as e:
        qilinguist.parsers.get_linguist_projects(args)
    assert e.value.message == "Cannot use project names when running " \
                               "outside a worktree"

def test_no_worktree_no_args(cd_to_tmpdir, args):
    args.projects = list()
    with pytest.raises(Exception) as e:
        qilinguist.parsers.get_linguist_projects(args)
    assert e.value.message == "You should specify at least a pml path " \
                              "when running outside a worktree"

def test_names_and_pml_from_worktree(linguist_worktree, args, monkeypatch):
    linguist_worktree.create_gettext_project("foo")
    linguist_worktree.tmpdir.join("bar.pml").write("""
<Package name="bar" />
""")
    args.projects = ["bar.pml", "foo"]
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 2
    foo = projects[0]
    assert foo.name == "foo"
    assert foo.linguas == ["fr_FR", "en_US"]
    bar = projects[1]
    assert bar.pml_path == linguist_worktree.tmpdir.join("bar.pml").strpath

def test_no_args_in_project(linguist_worktree, monkeypatch, args):
    foo_proj = linguist_worktree.create_gettext_project("foo")
    monkeypatch.chdir(foo_proj.path)
    args.projects = list()
    projects = qilinguist.parsers.get_linguist_projects(args)
    assert len(projects) == 1
    assert projects[0].name == "foo"
