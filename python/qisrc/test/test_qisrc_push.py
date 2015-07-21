## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.command
import qisrc.git

from qisrc.test.conftest import TestGitWorkTree, TestGit

import mock

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

def test_using_carbon_copy(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    # Need to fetch gerrit remote at least once for gerrit/master to exist
    foo_git.fetch("--all")
    foo_git.commit_file("a.txt", "a")
    with mock.patch.object(qisys.command, "call") as mocked_call:
        qisrc_action("push", "foo", "--cc", "jdoe")
    set_reviewers_args =  mocked_call.call_args_list[2][0][0][7]
    assert "jdoe" in set_reviewers_args

def test_alert_maintainers(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qiproject_xml = """\
<project version="3">
  <maintainer email="jdoe@company.com">John Doe</maintainer>
</project>"""
    git_server.push_file("foo.git", "qiproject.xml", qiproject_xml)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    # Need to fetch gerrit remote at least once for gerrit/master to exist
    foo_git.fetch("--all")
    foo_git.commit_file("a.txt", "a")
    with mock.patch.object(qisys.command, "call") as mocked_call:
        qisrc_action("push", "foo")
    set_reviewers_args =  mocked_call.call_args_list[3][0][0][7]
    assert "jdoe@company.com" in set_reviewers_args

def test_on_new_project(qisrc_action, git_server, tmpdir):
    foo_repo = git_server.create_repo("foo.git")
    foo_path = tmpdir.join("work").join("foo")
    foo_path.ensure(dir=True)
    git = qisrc.git.Git(foo_path.strpath)
    git.clone(foo_repo.clone_url)
    with qisys.sh.change_cwd(foo_path.strpath):
        qisrc_action("push")
    assert not foo_path.join("qiproject.xml").check(file=True)
