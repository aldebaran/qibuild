## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import qisrc.git
from qisrc.test.conftest import TestGitWorkTree
from qisrc.test.conftest import TestGit

def test_checkout_happy(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisrc_action("init", manifest_url)
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("checkout", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = qisrc.git.Git(foo_proj.path)
    assert foo_git.get_current_branch() == "devel"
    bar_proj = git_worktree.get_git_project("bar")
    bar_git = qisrc.git.Git(bar_proj.path)
    assert bar_git.get_current_branch() == "master"

def test_checkout_preserve_changes_when_checkout_fails(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "README.txt", "readme\n")
    qisrc_action("init", manifest_url)
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    readme = os.path.join(foo_proj.path, "README.txt")
    with open(readme, "w") as fp:
        fp.write("unstaged\n")
    rc = qisrc_action("checkout", "devel", retcode=True)
    assert rc != 0
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = qisrc.git.Git(foo_proj.path)
    assert foo_git.get_current_branch() == "master"
    # With --force:
    qisrc_action("checkout", "devel", "--force")
    assert foo_git.get_current_branch() == "devel"

def test_checkout_creates_at_correct_place(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    git_server.push_file("foo.git", "foo.txt", "this is foo")
    qisrc_action("init", manifest_url, "--branch", "devel")
    qisrc_action("checkout", "master")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    git.read_file("foo.txt")

def test_checkout_non_existing_branch(qisrc_action, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("init", manifest_url, "--branch", "master")
    error = qisrc_action("checkout", "does-not-exists", raises=True)
    assert "Update failed" in error

def test_skip_checkout_when_possible(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("init", manifest_url, "--branch", "master")
    qisrc_action("checkout", "devel")
    assert not record_messages.find("Checkout bar")

def test_using_force_when_not_an_a_branch(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "foo.txt", "this is foo")
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    git.checkout("HEAD~1")
    assert not git.get_current_branch()
    qisrc_action("checkout", "master", "--force")
    assert git.get_current_branch() == "master"

def test_retcode_when_checkout_fails(qisrc_action, git_server):
    git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)

    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")

    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    gitignore = os.path.join(foo_proj.path, ".gitignore")
    with open(gitignore, "w") as fp:
        fp.write("unstaged\n")

    rc = qisrc_action("checkout", "devel", retcode=True)
    assert rc != 0

def test_qisrc_checkout_when_no_group(qisrc_action, git_server):
    git_server.create_group("default", ["a", "b"], default=True)
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("rm-group", "default")
    git_server.switch_manifest_branch("devel")
    qisrc_action("checkout", "devel")

    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 0
