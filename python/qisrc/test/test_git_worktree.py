## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.qixml
import qisys.worktree
import qisrc.worktree

from qisrc.git_config import Remote

import pytest

def test_read_git_configs(tmpdir, test_git):
    tmpdir.mkdir("foo")
    tmpdir.mkdir("bar")
    wt = qisys.worktree.WorkTree(tmpdir.strpath)
    foo_proj = wt.add_project("foo")
    bar_proj = wt.add_project("bar")

    git = test_git(foo_proj.path)
    git.initialize()

    git = test_git(bar_proj.path)
    git.initialize(branch="next")

    tmpdir.join(".qi").join("git.xml").write(""" \
<qigit>
 <project src="foo" >
    <branch name="master" tracks="origin" />
 </project>
 <project src="bar" >
    <branch name="next" tracks="origin" />
    <remote name="origin" url="git@srv:bar.git" />
    <remote name="gerrit" url="john@gerrit:bar.git" review="true"/>
 </project>
</qigit>
""")


    git_wt = qisrc.worktree.GitWorkTree(wt)
    git_projects = git_wt.git_projects
    assert len(git_projects) == 2

    foo = git_wt.get_git_project("foo")
    assert foo.src == "foo"
    assert len(foo.branches) == 1
    assert foo.branches[0].name == "master"
    assert foo.branches[0].tracks == "origin"
    assert not foo.remotes

    bar = git_wt.get_git_project("bar")
    assert bar.src == "bar"
    assert len(bar.branches) == 1
    assert len(bar.remotes) == 2
    origin = bar.remotes[0]
    assert origin.name == "origin"
    assert origin.url == "git@srv:bar.git"
    gerrit = bar.remotes[1]
    assert gerrit.name == "gerrit"
    assert origin.url == "git@srv:bar.git"

def test_git_configs_are_persistent(git_worktree):
    foo = git_worktree.create_git_project("foo")
    upstream = Remote()
    upstream.name = "upstream"
    upstream.url = "git@srv:bar.git"
    foo.configure_remote(upstream)
    foo.configure_branch("master", tracks="upstream")
    foo.save_config()

    def check_config(foo):
        assert len(foo.remotes) == 1
        upstream = foo.remotes[0]
        assert upstream.name == "upstream"
        assert upstream.url == "git@srv:bar.git"
        assert len(foo.branches) == 1
        master = foo.branches[0]
        assert master.name == "master"
        assert master.tracks == "upstream"

    check_config(foo)
    wt2 = qisrc.worktree.GitWorkTree(git_worktree.worktree)
    foo2 = wt2.get_git_project("foo")
    check_config(foo2)

def test_clone_missing_simple(git_worktree, git_server):
    foo_repo = git_server.create_repo("foo")
    git_worktree.clone_missing(foo_repo)
    assert len(git_worktree.git_projects) == 1

def test_clone_missing_create_subdirs(git_worktree, git_server):
    foo_repo = git_server.create_repo("foo", src="long/path/to/foo")
    git_worktree.clone_missing(foo_repo)
    assert len(git_worktree.git_projects) == 1
    foo_proj = git_worktree.get_git_project("long/path/to/foo")
    assert foo_proj

def test_clone_missing_wrong_branch(git_worktree, git_server, record_messages):
    foo_repo = git_server.create_repo("foo")
    foo_repo.default_branch = "devel"
    git_worktree.clone_missing(foo_repo)
    assert not git_worktree.git_projects
    new_git_worktree = qisrc.worktree.GitWorkTree(git_worktree.worktree)
    assert not new_git_worktree.git_projects

def test_network_error_while_cloning(git_worktree, git_server):
    foo_repo = git_server.create_repo("foo")
    srv_temp = git_server.root.join("srv.temp")
    srv  = git_server.root.join("srv")
    srv.rename(srv_temp)
    git_worktree.clone_missing(foo_repo)
    assert not git_worktree.git_projects
    srv_temp.rename(srv)
    git_worktree.clone_missing(foo_repo)
    assert len(git_worktree.git_projects) == 1

def test_clone_missing_evil_nested(git_worktree, git_server):
    foo_bar_repo = git_server.create_repo("foo/bar")
    git_server.push_file("foo/bar", "bar.txt", "bar\n")
    foo_repo = git_server.create_repo("foo")
    git_worktree.clone_missing(foo_bar_repo)
    git_server.push_file("foo", "foo.txt", "foo\n")
    git_worktree.clone_missing(foo_repo)
    assert len(git_worktree.git_projects) == 2

def test_clone_missing_already_correct(git_worktree, git_server, record_messages):
    foo_repo = git_server.create_repo("FooBar")
    git_worktree.clone_missing(foo_repo)
    git_worktree.worktree.remove_project("FooBar")
    git_worktree.clone_missing(foo_repo)
    assert record_messages.find("ERROR") is None

def test_clone_missing_empty(git_worktree, git_server, record_messages):
    foo_repo = git_server.create_repo("foo")
    foo_path = git_worktree.tmpdir.ensure("foo", dir=True)
    git = qisrc.git.Git(foo_path.strpath)
    git.init()
    git_worktree.clone_missing(foo_repo)
    assert record_messages.find("WARN")

def test_read_groups(git_worktree, git_server):
    manifest_url = git_server.manifest_url
    git_server.create_group("foobar", ["foo", "bar"])
    git_server.create_group("mygroup", ["a", "b"])
    git_server.create_repo("other")
    git_worktree.configure_manifest(manifest_url)
    expected_srcs = ["a", "b", "bar", "foo"]
    expected = [git_worktree.get_git_project(x) for x in expected_srcs]
    actual = git_worktree.get_git_projects(groups=["foobar", "mygroup"])
    assert expected == actual
