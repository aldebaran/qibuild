## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.script
import qisrc.git
from qisrc.test.conftest import TestGitWorkTree

import os
import pytest

def test_in_new_directory(cd_to_tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")
    qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

def test_use_branch(cd_to_tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.switch_manifest_branch("devel")
    git_server.create_repo("onlyindevel.git")
    qisys.script.run_action("qisrc.actions.init",
                            [git_server.manifest_url, "--branch", "devel"])

    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 2

def test_no_review(qisrc_action, git_server):
    git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url, "--no-review")
    git_worktree = TestGitWorkTree()

    assert len(git_worktree.git_projects) == 1
    assert not git_worktree.manifest.review

    remotes = git_worktree.git_projects[0].remotes
    assert len(remotes) == 1
    assert not remotes[0].review

def test_no_review_activate_deactivate(qisrc_action, git_server):
    git_server.create_repo("foo.git", review=True)

    qisrc_action("init", git_server.manifest_url, "--no-review")
    qisrc_action("push", "-n", "foo")

    qisrc_action("init", git_server.manifest_url)
    qisrc_action("push", "-n", "foo")

    qisrc_action("init", git_server.manifest_url, "--no-review")
    qisrc_action("push", "-n", "foo")

def test_review_on_by_default(qisrc_action, git_server):
    git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()

    assert len(git_worktree.git_projects) == 1
    assert git_worktree.manifest.review

    remotes = git_worktree.git_projects[0].remotes
    assert len(remotes) == 2
    assert [remote for remote in remotes if remote.review]

def test_finish_configure_after_error(qisrc_action, git_server):
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
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("c")
    qisrc_action("init",  manifest_url)
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
    setup_re_add(qisrc_action, git_server)
    manifest_url =  git_server.manifest_url
    qisrc_action("init", manifest_url,"--group", "mygroup")
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3

def test_re_add_removed_by_hand(qisrc_action, git_server):
    manifest_url =  git_server.manifest_url
    setup_re_add(qisrc_action, git_server)
    git_worktree = TestGitWorkTree()
    c_path = git_worktree.get_git_project("c").path
    qisrc_action("init", manifest_url, "--group", "mygroup")
    qisys.sh.rm(c_path)
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert len(git_worktree.git_projects) == 3

def test_re_add_path_exists(qisrc_action, git_server):
    manifest_url =  git_server.manifest_url
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
    git_server.create_group("default", ["a"], default=True)
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    git_worktree = TestGitWorkTree()
    assert git_worktree.manifest.groups == ["default"]

def test_retcode_when_cloning_fails(qisrc_action, git_server):
    git_server.create_repo("bar.git")
    git_server.srv.join("bar.git").remove()
    rc = qisrc_action("init", git_server.manifest_url, retcode=True)
    assert rc != 0

def test_calling_init_twice(qisrc_action, git_server):
    git_server.create_repo("bar.git")
    qisrc_action("init", git_server.manifest_url)
    qisrc_action("init")

def test_explicit_worktree_root(qisrc_action, tmpdir):
    custom_worktree = tmpdir.join("custom_worktree")
    qisrc_action("init", "--worktree", custom_worktree.strpath)
    assert qisys.worktree.WorkTree(custom_worktree.strpath)

def test_relative_path(qisrc_action, tmpdir):
    git = qisrc.git.Git(str(tmpdir))
    git.init()
    manifest = open(str(tmpdir.join("manifest.xml")), "w")
    manifest.write("<manifest />")
    manifest.close()
    git.add("manifest.xml")
    git.commit("-m", "Initial commit")
    qisrc_action("init", os.path.relpath(str(tmpdir)))
    assert os.path.isfile(os.path.join(".qi", "manifests", "default", "manifest.xml"))
