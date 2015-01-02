## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qisrc.test.conftest import TestGitWorkTree, TestGit
import qisrc.git

def test_not_under_code_review(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push", "foo")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "origin", "master", raises=False)
    assert remote == "%s\trefs/heads/master" % sha1

def test_publish_changes(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push", "foo")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/for/master", raises=False)
    assert remote == "%s\trefs/for/master" % sha1
