# -*- encoding: utf-8 -*-
# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

"""Automatic testing for worktree

"""

import os

import py
import pytest
import mock

import qisys.sh
import qisys.worktree

# allow the existing foo/bar/baz names
# pylint: disable=blacklisted-name
# pylint: disable=unused-variable


def test_read_projects(tmpdir):
    tmpdir.mkdir("core").mkdir("naoqi")
    tmpdir.mkdir("lib").mkdir("libqi")
    xml_path = tmpdir.mkdir(".qi").join("worktree.xml")
    xml_path.write("""
<worktree>
    <project src="core/naoqi" />
    <project src="lib/libqi" />
</worktree>
""")
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    p_srcs = [p.src for p in worktree.projects]
    assert p_srcs == ["core/naoqi", "lib/libqi"]


def test_normalize_path(tmpdir):
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    foo_abs_path = tmpdir.join("bar").join("foo").strpath
    assert worktree.normalize_path(foo_abs_path) == "bar/foo"
    assert worktree.normalize_path("bar/foo") == "bar/foo"


def test_add_project_simple(worktree):
    # pylint: disable-msg=E1101
    tmp = py.path.local(worktree.root)
    tmp.mkdir("foo")
    worktree.add_project("foo")
    assert len(worktree.projects) == 1
    foo = worktree.get_project("foo")
    assert foo.src == "foo"


def test_fails_when_root_does_not_exists(tmpdir):
    non_existing = tmpdir.join("doesnotexist")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.worktree.WorkTree(non_existing.strpath)
    assert "does not exist" in str(e.value)


def test_ignore_src_dot(tmpdir):
    foo_path = tmpdir.mkdir("foo")
    tmpdir.join("foo", "qiproject.xml").write("""
<project>
  <project src="." />
</project>
""")
    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    worktree.add_project("foo")


def test_remove_project(worktree):
    # pylint: disable-msg=E1101
    tmp = py.path.local(worktree.root)
    foo_src = tmp.mkdir("foo")
    worktree.add_project("foo")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.worktree.WorkTreeError) as e:
        worktree.remove_project("bar")
    assert "No project in 'bar'" in e.value.message

    worktree.remove_project("foo")
    assert worktree.projects == list()

    worktree.add_project("foo")
    assert worktree.projects[0].src == "foo"

    worktree.remove_project("foo", from_disk=True)
    assert worktree.projects == list()
    assert not os.path.exists(foo_src.strpath)


def test_nested_qiprojects(tmpdir):
    a_project = tmpdir.mkdir("a")
    worktree_xml = tmpdir.mkdir(".qi").join("worktree.xml")
    worktree_xml.write("""
<worktree>
    <project src="a" />
</worktree>
""")

    a_xml = a_project.join("qiproject.xml")
    a_xml.write("""
<project name="a">
    <project src="b" />
</project>
""")

    b_project = a_project.mkdir("b")
    b_xml = b_project.join("qiproject.xml")
    b_xml.write("""
<project name="b">
    <project src="c" />
</project>
""")

    c_project = b_project.mkdir("c")
    c_xml = c_project.join("qiproject.xml")
    c_xml.write('<project name="c" />\n')

    worktree = qisys.worktree.WorkTree(tmpdir.strpath)
    assert len(worktree.projects) == 3
    assert [p.src for p in worktree.projects] == \
        ["a", "a/b", "a/b/c"]


def test_non_exiting_path_are_removed(tmpdir, interact):  # pylint: disable=unused-argument
    # all projects registered should exist:
    wt = qisys.worktree.WorkTree(tmpdir.strpath)
    a_path = tmpdir.mkdir("a")
    wt.add_project(a_path.strpath)
    a_path.remove()
    wt2 = qisys.worktree.WorkTree(tmpdir.strpath)
    assert wt2.projects == list()


def test_check_subprojects_exist(tmpdir):
    # subprojets in qiproject.xml should exist
    wt = qisys.worktree.WorkTree(tmpdir.strpath)
    a_path = tmpdir.mkdir("a")
    a_qiproject = a_path.join("qiproject.xml")
    a_qiproject.write(""" \
<project >
  <project src="b" />
</project>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.worktree.WorkTreeError) as e:
        wt.add_project("a")
    assert "invalid sub project" in e.value.message


def test_observers_are_notified(worktree):
    mock_observer = mock.Mock()
    worktree.register(mock_observer)
    worktree.create_project("foo")
    assert mock_observer.reload.called


def test_add_nested_projects(worktree):
    worktree.create_project("foo")
    tmpdir = worktree.tmpdir
    spam = tmpdir.mkdir("spam")
    spam.join("qiproject.xml").write(""" \
<project>
  <project src="eggs" />
</project>
""")
    spam.mkdir("eggs")
    worktree.add_project("spam")
    assert [p.src for p in worktree.projects] == ["foo", "spam", "spam/eggs"]

    worktree.remove_project("spam")
    assert [p.src for p in worktree.projects] == ["foo"]


def test_warns_on_nested_worktrees(tmpdir, record_messages):
    work1 = tmpdir.mkdir("work1")
    work1.mkdir(".qi")
    work2 = work1.mkdir("work2")
    work2.mkdir(".qi")
    wt2 = qisys.worktree.WorkTree(work2.strpath)
    assert record_messages.find("Nested worktrees")


def test_non_ascii_path(tmpdir):
    coffee_dir = tmpdir.mkdir("café")
    wt = qisys.worktree.WorkTree(coffee_dir.strpath)
