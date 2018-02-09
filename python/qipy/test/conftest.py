# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

from qisys.test.conftest import *  # pylint: disable=wildcard-import,unused-wildcard-import
import qipy.worktree

# pylint: disable=redefined-outer-name


class QiPyAction(TestAction):
    def __init__(self):
        super(QiPyAction, self).__init__("qipy.actions")

    def add_test_project(self, src):
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.worktree.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)

        worktree_project = self.worktree.add_project(src)
        python_project = qipy.worktree.new_python_project(self.worktree, worktree_project)
        return python_project

# pylint: disable-msg=E1101


@pytest.fixture
def qipy_action(cd_to_tmpdir):  # pylint: disable=unused-argument
    res = QiPyAction()
    return res
