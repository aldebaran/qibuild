#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.sh
import qidoc.convert
from qidoc.test.conftest import TestDocWorkTree


def test_convert_handle_src(worktree):
    """ Test Convert Handle Src """
    foo_proj = worktree.create_project("foo")
    _bar_proj = worktree.create_project("foo/bar")
    xml = """
<project>
  <doxydoc name="a_doxy" src="bar" />
</project>
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)
    qidoc.convert.convert_project(foo_proj)
    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 1
    assert doc_projects[0].src == "foo/bar"


def test_convert_add_subprojects(worktree):
    """ Test Convert Add SubProjects """
    foo_proj = worktree.create_project("foo")
    bar_path = os.path.join(foo_proj.path, "bar")
    qisys.sh.mkdir(bar_path)
    xml = """
<project name="foo" >
  <doxydoc name="a_doxy" src="bar" />
</project>
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)
    qidoc.convert.convert_project(foo_proj)
    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 1
    assert doc_projects[0].src == "foo/bar"


def test_convert_keep_dest(worktree):
    """ Test Convert Keep Dest """
    foo_proj = worktree.create_project("foo")
    bar_path = os.path.join(foo_proj.path, "bar")
    qisys.sh.mkdir(bar_path)
    xml = """
<project name="foo" >
  <doxydoc name="a_doxy" src="bar" dest="ref/bar" />
</project>
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)
    qidoc.convert.convert_project(foo_proj)
    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 1
    assert doc_projects[0].src == "foo/bar"
    assert doc_projects[0].dest == "ref/bar"


def test_convert_src_dot(worktree):
    """ Test Convert Src Dot """
    foo_proj = worktree.create_project("foo")
    xml = """
<project>
  <doxydoc name="a_doxy" src="." />
</project>
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)
    qidoc.convert.convert_project(foo_proj)
    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert len(doc_projects) == 1
    assert doc_projects[0].src == "foo"


def test_convert_template(worktree):
    """ Test Convert Template """
    foo_proj = worktree.create_project("foo")
    xml = """\n<project template_repo="true" />\n"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)
    doc_worktree = TestDocWorkTree()
    _doc_projects = doc_worktree.doc_projects
    assert doc_worktree.template_project.src == "foo"
