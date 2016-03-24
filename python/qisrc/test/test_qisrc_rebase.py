## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import pytest

import qisys.error
from qisrc.test.conftest import TestGitWorkTree
from qisrc.test.conftest import TestGit

def test_happy_rebase(git_server, qisrc_action):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "master.txt", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("devel.txt", "devel")
    git.push()
    git.fetch()
    qisrc_action("rebase", "--branch", "master", "--all")
    rc, out = git.log("--pretty=oneline", raises=False)
    assert len(out.splitlines()) == 3

def test_rebase_conflict(git_server, qisrc_action):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "foo.txt", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("foo.txt", "devel")
    git.push()
    _, before = git.call("show", raises=False)
    git.fetch()
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qisrc_action("rebase", "--branch", "master", "--all")
    assert " * foo" in e.value.message
    _, after = git.call("show", raises=False)
    assert after == before

def test_raises_when_not_on_correct_branch(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.checkout("-B", "perso")
    error = qisrc_action("rebase", "--branch", "master", "--all", raises=True)
    assert " * foo" in error
    assert record_messages.find("skipped")

def test_when_moved(git_server, qisrc_action, record_messages):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    git_server.move_repo("foo", "lib/foo")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "master.txt", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("lib/foo")
    git = TestGit(foo_proj.path)
    git.commit_file("devel.txt", "devel")
    git.push()
    qisrc_action("rebase", "--branch", "master", "--all")
    rc, out = git.log("--pretty=oneline", raises=False)
    assert len(out.splitlines()) == 3

def test_when_not_up_to_date(git_server, qisrc_action):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "master.txt", "devel")
    retcode = qisrc_action("rebase", "--branch", "master", "--all", retcode=True)
    assert retcode == 0

def test_when_ahead(git_server, qisrc_action):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("devel.txt", "devel")
    git.push()
    qisrc_action("rebase", "--all")

def test_push_after_rebase(git_server, git_worktree, qisrc_action, interact):
    git_server.create_repo("foo")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    git_server.push_file("foo", "master.txt", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    git_server.push_file("foo", "master.txt", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.commit_file("devel.txt", "devel")
    git.fetch()
    git.push("origin", "devel")
    interact.answers = [True]
    qisrc_action("rebase", "--branch", "master", "--push", "--all")
    local_sha1 = git.get_ref_sha1("refs/heads/devel")
    remote_sha1 = git.get_ref_sha1("refs/remotes/origin/devel")
    assert local_sha1 == remote_sha1


def test_only_rebase_forked_projects(git_server, git_worktree, qisrc_action, record_messages):
    git_server.create_repo("foo")
    git_server.create_repo("bar")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo", "devel")
    git_server.push_file("foo", "master.txt", "devel")
    qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    record_messages.reset()
    qisrc_action("rebase", "--branch", "master", "--all")
    assert not record_messages.find("bar")
