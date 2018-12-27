#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" ConfTest """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import py
import pytest

import qibuild.worktree
import qisys.worktree
from qisys.test.conftest import *  # pylint:disable=W0401,W0614
from qitoolchain.test.conftest import *  # pylint:disable=W0401,W0614


class TestBuildWorkTree(qibuild.worktree.BuildWorkTree):
    """ A subclass of qisrc.worktree.WorkTree that can create git projects """

    __test__ = False  # Tell PyTest to ignore this Test* named class: This is as test to collect

    def __init__(self, worktree=None):
        """ TestBuildWorkTree Init """
        if not worktree:
            worktree = TestWorkTree()
        super(TestBuildWorkTree, self).__init__(worktree)

    @property
    def tmpdir(self):
        """ Tmp Dir """
        return py.path.local(self.root)  # pylint:disable=no-member

    def create_project(self, name, src=None,
                       build_depends=None, run_depends=None, test_depends=None):
        """ Create a new build project """
        if not build_depends:
            build_depends = list()
        if not run_depends:
            run_depends = list()
        if not test_depends:
            test_depends = list()
        if not src:
            src = name
        proj_path = self.tmpdir.join(*src.split("/"))
        proj_path.ensure(dir=True)
        xml = """ \
<project version="3">
  <qibuild name="{name}">
    <depends buildtime="true" runtime="false" testtime="false" names="{buildtime_names}" />
    <depends buildtime="false" runtime="true" testtime="false" names="{runtime_names}" />
    <depends buildtime="false" runtime="false" testtime="true" names="{testtime_names}" />
  </qibuild>
</project>
"""
        xml = xml.format(name=name,
                         buildtime_names=" ".join(build_depends),
                         runtime_names=" ".join(run_depends),
                         testtime_names=" ".join(test_depends))
        proj_path.join("qiproject.xml").write(xml)
        cmake = """ \
cmake_minimum_required(VERSION 2.8)
project({name} C)
find_package(qibuild)
qi_create_bin({name} main.c)

"""
        cmake = cmake.format(name=name)
        main_c = """ \
int main()
{
  return 0;
}
"""
        proj_path.join("CMakeLists.txt").write(cmake)
        proj_path.join("main.c").write(main_c)
        self.worktree.add_project(src)
        return self.get_build_project(name)

    def add_test_project(self, src):
        """
        Copy a project, reading the sources from qibuild/test/projects/<src>
        If qibuild project name cannot be read from qiproject.xml,
        return None (useful for qibuild convert tests)
        """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)
        worktree_project = self.worktree.add_project(src)
        build_project = qibuild.worktree.new_build_project(self, worktree_project)
        return build_project


@pytest.fixture
def build_worktree(cd_to_tmpdir):
    """ Build Worktree """
    return TestBuildWorkTree()


@pytest.fixture
def qibuild_action(cd_to_tmpdir):
    """ QiBuild Action """
    return QiBuildAction()


class QiBuildAction(TestAction):
    """ QiBuildAction Class """

    def __init__(self):
        """ QiBuildAction Init """
        super(QiBuildAction, self).__init__("qibuild.actions")
        self.build_worktree = TestBuildWorkTree()

    def add_test_project(self, name):
        """ Add a test project using a project path in <this_dir>/projects/ """
        return self.build_worktree.add_test_project(name)

    def create_project(self, name, **kwargs):
        """ Delegates to TestBuildWorkTree.create_project """
        return self.build_worktree.create_project(name, **kwargs)

    def reload_worktree(self):
        """ Reload the worktree. Useful when an *other* BuildWorkTree has changed the cache """
        self.build_worktree = TestBuildWorkTree()

    @property
    def tmpdir(self):
        """ Tmp Dir """
        return self.build_worktree.tmpdir


class FakeProcess(object):
    """ Fake subprocess.Popen return """

    def __init__(self, returncode, stdout=None, stderr=None):
        """ FakeProcess Init """
        self.returncode = int(returncode)
        self.stdout = str(stdout) if stdout else stdout
        self.stderr = str(stderr) if stderr else stderr

    def communicate(self):
        """ Communicate """
        return self.stdout, self.stderr

    def wait(self):
        """ Wait """
        return self.returncode
