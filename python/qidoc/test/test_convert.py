## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisys.sh

import qidoc.convert
from qidoc.test.conftest import TestDocWorkTree
from qibuild.test.conftest import TestBuildWorkTree

def test_convert_handle_src(worktree):
    foo_proj = worktree.create_project("foo")
    bar_proj = worktree.create_project("foo/bar")
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
    foo_proj = worktree.create_project("foo")
    xml = """
<project template_repo="true" />
"""
    with open(foo_proj.qiproject_xml, "w") as fp:
        fp.write(xml)

    doc_worktree = TestDocWorkTree()
    doc_projects = doc_worktree.doc_projects
    assert doc_worktree.template_project.src == "foo"
