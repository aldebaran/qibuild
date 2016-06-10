## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.command
import qisys.sh
import qisrc.git
import qisys.command
import pytest

from qisrc.test.conftest import TestGitWorkTree, TestGit

import mock

def test_not_under_code_review_ask_user(qisrc_action, git_server, interact):
    foo_repo = git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    interact.answers = [False, True]
    qisrc_action("push", "--project", "foo")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "origin", "master", raises=False)
    assert remote != "%s\trefs/heads/master" % sha1
    qisrc_action("push", "--project", "foo")
    (_, remote) = foo_git.call("ls-remote", "origin", "master", raises=False)
    assert remote == "%s\trefs/heads/master" % sha1

def test_not_under_code_review_with_no_review(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push", "--no-review", "--project", "foo")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "origin", "master", raises=False)
    assert remote == "%s\trefs/heads/master" % sha1

def test_using_dash_y(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push",  "--project", "foo", "-y")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "origin", "master", raises=False)
    assert remote == "%s\trefs/heads/master" % sha1

def test_using_dash_f_without_review(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git")
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push",  "--project", "foo", "-y")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "origin", "refs/heads/master", raises=False)

    foo_git.commit("--amend", "-mfoobar")
    _, new_sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)

    # pylint:disable-msg=E1101
    with pytest.raises(qisys.command.CommandFailedException):
        qisrc_action("push", "--project", "foo", "-y")

    (_, remote) = foo_git.call("ls-remote", "origin", "refs/heads/master", raises=False)

    assert remote == "%s\trefs/heads/master" % sha1

    qisrc_action("push",  "--project", "foo", "-y", "-f")
    (_, remote) = foo_git.call("ls-remote", "origin", "refs/heads/master", raises=False)
    assert remote == "%s\trefs/heads/master" % new_sha1

def test_using_dash_f_with_review(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push",  "--project", "foo", "--no-review")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/heads/master", raises=False)

    foo_git.commit("--amend", "-mfoobar")
    _, new_sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)

    # pylint:disable-msg=E1101
    with pytest.raises(qisys.command.CommandFailedException):
        qisrc_action("push", "--project", "foo", "--no-review")

    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/heads/master", raises=False)
    assert remote.split()[0] == sha1

    qisrc_action("push",  "--project", "foo", "-f")
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/heads/master", raises=False)
    assert remote.split()[0] == new_sha1

def test_publish_changes(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push", "--project", "foo")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/for/master", raises=False)
    assert remote == "%s\trefs/for/master" % sha1

def test_publish_drafts(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push", "--project", "foo", "--draft")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/drafts/master", raises=False)
    assert remote == "%s\trefs/drafts/master" % sha1

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
        qisrc_action("push", "--project", "foo", "--cc", "jdoe")
    set_reviewers_args =  mocked_call.call_args_list[2][0][0][7]
    assert "jdoe" in set_reviewers_args

def test_alert_maintainers(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qiproject_xml = """\
<project format="3">
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
        qisrc_action("push", "--project", "foo")
    set_reviewers_args =  mocked_call.call_args_list[-1][0][0][-1] # Last argument of last command
    assert "jdoe" in set_reviewers_args
    assert not "@company.com" in set_reviewers_args

def test_on_new_project(qisrc_action, git_server, tmpdir, interact):
    foo_repo = git_server.create_repo("foo.git")
    foo_path = tmpdir.join("work").join("foo")
    foo_path.ensure(dir=True)
    git = qisrc.git.Git(foo_path.strpath)
    git.clone(foo_repo.clone_url)
    interact.answers = [True]
    with qisys.sh.change_cwd(foo_path.strpath):
        qisrc_action("push", retcode=True)
    assert not foo_path.join("qiproject.xml").check(file=True)

def test_pushing_from_perso_branch(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.checkout("-b", "perso")
    foo_git.commit_file("a.txt", "a")
    qisrc_action("push", "--project", "foo", "master")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/for/master", raises=False)
    assert remote == "%s\trefs/for/master" % sha1

def test_pushing_custom_ref(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.checkout("-b", "perso")
    foo_git.commit_file("a.txt", "a")
    _, sha1 = foo_git.call("log", "-1", "--pretty=%H", raises=False)
    foo_git.commit_file("b.txt", "b")
    qisrc_action("push", "--project", "foo", "HEAD~1:master")
    (_, remote) = foo_git.call("ls-remote", "gerrit", "refs/for/master", raises=False)
    assert remote == "%s\trefs/for/master" % sha1

def test_orphaned_project(qisrc_action, git_server, record_messages):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qiproject_xml = """\
<project version="3">
  <maintainer>ORPHANED</maintainer>
</project>"""
    git_server.push_file("foo.git", "qiproject.xml", qiproject_xml)

    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)

    # Need to fetch gerrit remote at least once for gerrit/master to exist
    foo_git.fetch("--all")
    foo_git.commit_file("a.txt", "a")
    record_messages.reset()
    qisrc_action("push", "--project", "foo")
    assert record_messages.find("Project is orphaned")

def test_no_reviewers_when_no_review(qisrc_action, git_server):
    foo_repo = git_server.create_repo("foo.git", review=True)
    qiproject_xml = """\
<project format="3">
  <maintainer email="jdoe@company.com">John Doe</maintainer>
</project>"""
    git_server.push_file("foo.git", "qiproject.xml", qiproject_xml)
    qisrc_action("init", git_server.manifest_url)
    git_worktree = TestGitWorkTree()
    foo_proj = git_worktree.get_git_project("foo")
    foo_git = TestGit(foo_proj.path)
    foo_git.commit_file("a.txt", "a")
    with mock.patch("qisrc.review.set_reviewers") as set_reviewers:
        qisrc_action("push", "--no-review", "--project", "foo")
        assert not set_reviewers.called

