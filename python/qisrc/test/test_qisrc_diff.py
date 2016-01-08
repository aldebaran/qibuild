## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.git

from qisrc.test.conftest import TestGitWorkTree

def test_simple(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "a.txt",
                         "this is devel\n", branch="devel",
                         message="start developing")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("diff", "--all", "master")
    assert record_messages.find("a.txt | 1 +")
    record_messages.reset()
    qisrc_action("diff", "--all", "--patch", "master")
    assert record_messages.find("\+this is devel")


def test_fail(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "a.txt",
                         "this is devel\n", branch="devel",
                         message="start developing")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    git.call("remote", "rm", "origin")
    qisrc_action("diff", "--all", "master")
    assert record_messages.find("git diff --stat")
    assert record_messages.find("unknown revision")
