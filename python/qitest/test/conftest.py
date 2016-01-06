## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qibuild.test.conftest import *
from qisys.test.conftest import TestAction

import qibuild.find

import pytest

# pylint: disable-msg=E1103
@pytest.fixture
def compiled_tests(build_worktree):
    testme_proj = build_worktree.add_test_project("testme")
    testme_proj.configure()
    testme_proj.build()

    tests = list()
    paths = [testme_proj.sdk_directory]
    for name in ["ok", "fail", "segfault", "timeout"]:
        test = {
            "name" : name,
            "cmd" : [qibuild.find.find_bin(paths, name)],
        }
        if name == "timeout":
            test["timeout"] = 1
        tests.append(test)
    return tests

# pylint: disable-msg=E1103
@pytest.fixture
def qitest_action(cd_to_tmpdir):
    res = QiTestAction()
    return res

class QiTestAction(TestAction):
    def __init__(self):
        super(QiTestAction, self).__init__("qitest.actions")
        self.worktree = TestWorkTree()

    def add_test_project(self, src):
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.worktree.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)
        worktree_project = self.worktree.add_project(src)

        return worktree_project
