#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Init """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest
import py

import qisys.script
import qisrc.git
from qisrc.test.conftest import TestGit
from qisrc.test.conftest import TestGitWorkTree


def test_in_new_directory(cd_to_tmpdir, git_server):
    """ Test In New Directory """
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2


def test_use_branch(cd_to_tmpdir, git_server):
    """ Test Use Branch """
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.create_repo("onlyindevel.git")
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url, "--branch", "devel"])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2


def test_no_review(qisrc_action, git_server):
    """ Test No Review """
    git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url, "--no-review")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
    assert not git_worktree.manifest.review
    remotes = git_worktree.git_projects[0].remotes
    assert len(remotes) == 1
    assert not remotes[0].review


def test_no_review_activate_deactivate(qisrc_action, git_server):
    """ Test No Review Activate Deactivate """
    git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url, "--no-review")
    qisrc_action("push", "-n", "--project", "foo")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("push", "-n", "--project", "foo")
    qisrc_action("init", git_server.manifest_url, "--no-review")
    qisrc_action("push", "-n", "--project", "foo")


def test_review_on_by_default(qisrc_action, git_server):
    """ Test Review On By Default """
    git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 1
    assert git_worktree.manifest.review
    remotes = git_worktree.git_projects[0].remotes
    assert len(remotes) == 2
    assert [remote for remote in remotes if remote.review]


def test_finish_configure_after_error(qisrc_action, git_server):
    """ Test Finish Configure After Error """
    # bogus repo can't be configured, but we don't want configuration to be
    # interrupted
    git_server.create_repo("foo.git", review=True)
    git_server.manifest.add_repo("bogus", None, ["origin", "gerrit"])
    git_server.create_repo("bar.git", review=True)
    rc = qisrc_action("init", git_server.manifest_url, retcode=True)
    assert rc != 0
    git_worktree = TestGitWorkTree()
    assert git_worktree.manifest


def test_reconfigure(qisrc_action, git_server):
    """ Test ReConfigure """
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3
    qisrc_action("init", manifest_url, "-g", "mygroup")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2


def setup_re_add(qisrc_action, git_server):
    """ Helper for test_re_add_projects """
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("init", manifest_url)


def test_re_add_happy_path(qisrc_action, git_server):
    """ Test Re Add Happy Path """
    setup_re_add(qisrc_action, git_server)
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_re_add_removed_by_hand(qisrc_action, git_server):
    """ Test Add Removed By Hand """
    manifest_url = git_server.manifest_url
    setup_re_add(qisrc_action, git_server)
    git_worktree = TestGitWorkTree()
    c_path = git_worktree.get_git_project("c").path
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisys.sh.rm(c_path)
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_re_add_path_exists(qisrc_action, git_server):
    """ Test Re Add Path Exists """
    manifest_url = git_server.manifest_url
    setup_re_add(qisrc_action, git_server)
    git_worktree = TestGitWorkTree()
    c_path = git_worktree.get_git_project("c").path
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisys.sh.rm(c_path)
    qisys.sh.mkdir(c_path)
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_stores_default_group(qisrc_action, git_server):
    """ Test Stores Default Group """
    git_server.create_group("default", ["a"], default=True)
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert git_worktree.manifest.groups == ["default"]


def test_retcode_when_cloning_fails(qisrc_action, git_server):
    """ Test RetCode When Cloning Fails """
    git_server.create_repo("bar.git")
    git_server.srv.join("bar.git").remove()
    rc = qisrc_action("init", git_server.manifest_url, retcode=True)
    assert rc != 0


def test_calling_init_twice(qisrc_action, git_server):
    """ Test Calling Init Twice """
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("init")


def test_explicit_worktree_root(qisrc_action, tmpdir):
    """ Test Explicit WorkTree """
    custom_worktree = tmpdir.join("custom_worktree")
    qisrc_action("init", "--worktree", custom_worktree.strpath)
    assert qisys.worktree.WorkTree(custom_worktree.strpath)


def test_manifest_branch_does_not_exist(qisrc_action, git_server):
    """ Test Manifest Branch Does Not Exist """
    git_server.create_repo("bar.git")
    _manifest_url = git_server.manifest_url
    with pytest.raises(Exception) as e:
        qisrc_action("init", git_server.manifest_url, "--branch", "devel")
    assert "origin/devel" in e.value.message


def test_relative_path(qisrc_action, tmpdir):
    """ Test Relative Path """
    git = qisrc.git.Git(tmpdir.strpath)
    git.init()
    manifest = tmpdir.join("manifest.xml")
    manifest.write("<manifest />")
    git.add("manifest.xml")
    git.commit("-m", "Initial commit")
    qisrc_action("init", os.path.relpath(tmpdir.strpath))
    assert os.path.isfile(os.path.join(".qi", "manifests", "default", "manifest.xml"))


def test_using_checkout_after_no_review(qisrc_action, git_server):
    """ Test Using Checkout After No Review """
    git_server.create_repo("foo", review=True)
    qisrc_action("init", git_server.manifest_url, "--no-review")
    git_server.switch_manifest_branch("devel")
    qisrc_action("checkout", "devel")
    git_worktree = TestGitWorkTree()
    foo1 = git_worktree.get_git_project("foo")
    assert not foo1.review


def test_all(qisrc_action, git_server):
    """ Test All """
    git_server.create_group("default", ["a.git", "b.git"])
    git_server.create_repo("c.git")
    qisrc_action("init", git_server.manifest_url, "--all")
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3


def test_tags(qisrc_action, git_server):
    """ Test Tags """
    git_server.create_repo("foo.git")
    git_server.push_file("foo.git", "a.txt", "a")
    git_server.push_tag("foo.git", "v0.1")
    git_server.push_file("foo.git", "b.txt", "b")
    git_server.set_fixed_ref("foo.git", "v0.1")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    git = TestGit(foo_proj.path)
    _, sha1 = git.call("rev-parse", "HEAD", raises=False)
    expected = git.get_ref_sha1("refs/tags/v0.1")
    assert sha1 == expected


def test_init_submodule(qisrc_action, git_server):
    """ Test Sync Clones New Repos """
    git_server.create_repo("foo.git")
    bar_remote_path = git_server._create_repo("bar.git")  # do not add it to the manifest
    git_server.push_file("bar.git", "README", "This is bar\n")
    git_server.push_submodule("foo.git", bar_remote_path, "bar")
    qisrc_action("init", git_server.manifest_url)
    cwd = py.path.local(os.getcwd())  # pylint:disable=no-member
    bar_local_path = cwd.join("foo").join("bar")
    assert bar_local_path.isdir()
    assert bar_local_path.join("README").isfile()
