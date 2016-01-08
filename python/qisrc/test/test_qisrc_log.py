## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.git

from qisrc.test.conftest import TestGitWorkTree

def test_calls_git_log(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "devel",
                         "this is devel\n", branch="devel",
                         message="start developing")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("log", "--all", "master")
    assert record_messages.find("start developing")

def test_when_not_on_a_branch(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "devel",
                         "this is devel\n", branch="devel",
                         message="start developing")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_worktree = TestGitWorkTree()
    foo = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo.path)
    git.checkout("HEAD~1")
    record_messages.reset()
    qisrc_action("log", "--all", "master")
    assert record_messages.find("Not on a branch")

def test_skips_when_no_diff(git_server, qisrc_action, record_messages):
    git_server.create_repo("repo_foo.git")
    git_server.create_repo("repo_bar.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("repo_foo.git", "devel")
    git_server.change_branch("repo_bar.git", "devel")
    git_server.push_file("repo_foo.git", "devel", "this is devel\n", branch="devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("log", "--all", "master")
    assert record_messages.find("repo_foo")
    assert not record_messages.find("repo_bar")

def test_display_markers_when_diverged(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "a.txt", "devel", branch="devel",
                         message="on devel")
    git_server.push_file("foo.git", "a.txt", "master", branch="master",
                          message="on master", fast_forward=False)
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("log", "--all", "master")
    assert record_messages.find("> .*[a-f0-8]+.* on devel")
    assert record_messages.find("< .*[a-f0-8]+.* on master")
