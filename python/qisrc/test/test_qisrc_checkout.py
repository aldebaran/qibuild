#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Checkout """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisrc.git
from qisrc.test.conftest import TestGit
from qisrc.test.conftest import TestGitWorkTree


def test_checkout_happy(qisrc_action, git_server):
    """ Test Checkout Happy """
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
    """ Test Checkout Preserve Changes When Checkout Fails """
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
    """ Test Checkout Creates At Correct Place """
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
    """ Test Checkout Non Existing Branch """
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("init", manifest_url, "--branch", "master")
    error = qisrc_action("checkout", "does-not-exists", raises=True)
    assert "Update failed" in error


def test_skip_checkout_when_possible(qisrc_action, git_server, record_messages):
    """ Test Skip Checkout Wen Possible """
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    git_server.switch_manifest_branch("devel")
    git_server.change_branch("foo.git", "devel")
    qisrc_action("init", manifest_url, "--branch", "master")
    qisrc_action("checkout", "devel")
    assert not record_messages.find("Checkout bar")


def test_using_force_when_not_a_branch(qisrc_action, git_server):
    """ Test Using Force When Not a Branch """
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
    """ Test RetCode When Checkout """
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
    """ Test QiSrc Checkout When No Group """
    git_server.create_group("default", ["a", "b"], default=True)
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("rm-group", "default")
    git_server.switch_manifest_branch("devel")
    qisrc_action("checkout", "devel")
    git_worktree = TestGitWorkTree()
    assert not git_worktree.git_projects


def test_qisrc_checkout_with_ref_to_branch(qisrc_action, git_server):
    """ Test QiSrc Checkout With Ref To Branch """
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", manifest_url)
    git_server.switch_manifest_branch("devel")
    git_server.set_branch("foo.git", "devel")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    assert sha1 == expected
    qisrc_action("checkout", "devel")
    foo_git = qisrc.git.Git(foo_proj.path)
    assert foo_git.get_current_branch() == "devel"
    bar_proj = git_worktree.get_git_project("bar")
    bar_git = qisrc.git.Git(bar_proj.path)
    assert bar_git.get_current_branch() == "master"


def test_qisrc_checkout_with_branch_to_ref(qisrc_action, git_server):
    """ Test QiSrc Checkout With Branch to Ref """
    manifest_url = git_server.manifest_url
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.push_tag("bar.git", "v0.2")
    git_server.push_file("bar.git", "c.txt", "b")
    qisrc_action("init", manifest_url)
    git_server.switch_manifest_branch("devel")
    git_server.set_fixed_ref("foo.git", "v0.1")
    git_server.set_fixed_ref("bar.git", "v0.2")
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    assert git.get_current_branch() == "master"
    qisrc_action("checkout", "devel")
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    assert sha1 == expected
    bar_proj = git_worktree.get_git_project("bar")
    bar_git = qisrc.git.Git(bar_proj.path)
    _, sha1 = bar_git.call("rev-parse", "HEAD", raises=False)
    expected = bar_git.get_ref_sha1("refs/tags/v0.2")
    assert sha1 == expected
