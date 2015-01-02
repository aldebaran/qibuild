## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
def test_qisrc_foreach(qisrc_action, record_messages):
    worktree = qisrc_action.worktree
    worktree.create_project("not_in_git")
    git_worktree = qisrc_action.git_worktree
    git_worktree.create_git_project("git_project")
    qisrc_action("foreach", "ls")
    assert not record_messages.find("not_in_git")
    assert record_messages.find("git_project")
    record_messages.reset()
    qisrc_action("foreach", "ls", "--all")
    assert record_messages.find("not_in_git")
    assert record_messages.find("git_project")
