#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import py
import bs4
import pytest

import qidoc.worktree
import qisys.qixml
from qisys.test.conftest import *  # pylint:disable=W0401,W0614


class TestDocWorkTree(qidoc.worktree.DocWorkTree):
    """ A subclass of DocWorkTree that can create doc projects """

    __test__ = False  # Tell PyTest to ignore this Test* named class: This is as test to collect

    def __init__(self, worktree=None):
        """ TestDocWorkTree Init """
        if not worktree:
            worktree = TestWorkTree()
        super(TestDocWorkTree, self).__init__(worktree)

    def add_templates(self):
        """ Add Templates """
        self.add_test_project("templates")

    @property
    def tmpdir(self):
        """ Tmp Dir """
        return py.path.local(self.root)  # pylint:disable=no-member

    def create_doc_project(self, name, src=None, depends=None, doc_type="sphinx", dest=None):
        """ Create Doc Project """
        if not depends:
            depends = list()
        if not src:
            src = name
        proj_path = self.tmpdir.join(*src.split("/"))
        proj_path.ensure(dir=True)
        project_elem = qisys.qixml.etree.Element("project")
        project_elem.set("version", "3")
        qidoc_elem = qisys.qixml.etree.Element("qidoc")
        qidoc_elem.set("name", name)
        qidoc_elem.set("type", doc_type)
        project_elem.append(qidoc_elem)
        for dep_name in depends:
            dep_elem = qisys.qixml.etree.Element("depends")
            dep_elem.set("name", dep_name)
            qidoc_elem.append(dep_elem)
        if dest:
            qidoc_elem.set("dest", dest)
        qiproject_xml = proj_path.join("qiproject.xml").strpath
        qisys.qixml.write(project_elem, qiproject_xml)
        self.worktree.add_project(src)
        return self.get_doc_project(name)

    def create_sphinx_project(self, name, src=None, depends=None):
        """ Create Sphinx Project """
        return self.create_doc_project(name, src=src, depends=depends,
                                       doc_type="sphinx")

    def create_doxygen_project(self, name, src=None, depends=None):
        """ Create Doxygen Project """
        return self.create_doc_project(name, src=src, depends=depends,
                                       doc_type="doxygen")

    def add_test_project(self, src):
        """
        Copy a project, reading sources from qidoc/test/projects.
        Can return None when testing qidoc2 retro-compat.
        """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)

        worktree_project = self.worktree.add_project(src)
        doc_project = qidoc.worktree.new_doc_project(self, worktree_project)
        return doc_project


class QiDocAction(TestAction):
    """ QiDocAction Class """

    def __init__(self):
        """ QiDocAction Init """
        super(QiDocAction, self).__init__("qidoc.actions")
        self.doc_worktree = TestDocWorkTree()

    def add_test_project(self, *args, **kwargs):
        """ Add Test Project """
        return self.doc_worktree.add_test_project(*args, **kwargs)

    def create_sphinx_project(self, *args, **kwargs):
        """ Create Sphinx Project """
        return self.doc_worktree.create_sphinx_project(*args, **kwargs)

    def create_doxygen_project(self, *args, **kwargs):
        """ Create Docygen Project """
        return self.doc_worktree.create_doxygen_project(*args, **kwargs)


def find_link(html_path, text):
    """ Find Link """
    with open(html_path, "r") as fp:
        data = fp.read()
    soup = bs4.BeautifulSoup(data, "html.parser")
    link = soup.find("a", text=text)
    target = link.attrs["href"]
    target_path = target.split("#")[0]
    return target_path


@pytest.fixture
def doc_worktree(cd_to_tmpdir):
    """ Doc WorkTree """
    return TestDocWorkTree()


@pytest.fixture
def qidoc_action(cd_to_tmpdir):
    """ QiDoc Action """
    return QiDocAction()
