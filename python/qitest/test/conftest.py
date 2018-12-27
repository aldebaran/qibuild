#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qisys
from qisys.test.conftest import TestAction
import qibuild.find
from qibuild.test.conftest import TestWorkTree, cd_to_tmpdir


@pytest.fixture
def compiled_tests(build_worktree):
    """ Compiled Tests """
    testme_proj = build_worktree.add_test_project("testme")
    testme_proj.configure()
    testme_proj.build()
    tests = list()
    paths = [testme_proj.sdk_directory]
    for name in ["ok", "fail", "segfault", "timeout"]:
        test = {
            "name": name,
            "cmd": [qibuild.find.find_bin(paths, name)],
        }
        if name == "timeout":
            test["timeout"] = 1
        tests.append(test)
    return tests


@pytest.fixture
def qitest_action(cd_to_tmpdir):
    """ QiTest Action """
    return QiTestAction()


class QiTestAction(TestAction):
    """ QiTestAction """

    def __init__(self):
        """ QiTestAction Init """
        super(QiTestAction, self).__init__("qitest.actions")
        self.worktree = TestWorkTree()

    def add_test_project(self, src):
        """ Add Test Project """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.worktree.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)
        return self.worktree.add_project(src)
