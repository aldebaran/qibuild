## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qisrc.test.conftest import TestGitWorkTree

def test_qisrc_rm_group(qisrc_action, git_server):
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_group("foobar", ["foo", "bar", "baz"])
    qisrc_action("init", git_server.manifest_url,
                "--group", "mygroup",
                "--group", "foobar")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 5
    qisrc_action("rm-group", "foobar")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

