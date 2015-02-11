## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.script
import qisrc.git
from qisys.test.conftest import TestWorkTree

def test_simple(qisrc_action):
    qisrc_action("create", "foo")
    # cannot use qibuild_action fixture without creating recursive
    # dependencies ...
    qisys.script.run_action("qibuild.actions.configure", ["foo"])

def test_with_git(qisrc_action):
    qisrc_action("create", "foo", "--git")
    worktree = TestWorkTree()
    foo_proj = worktree.get_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    ret, out = git.call("show", "HEAD", raises=False)
    assert ret == 0
    assert ".gitignore" in out

def test_in_subdir(qisrc_action):
    qisrc_action.tmpdir.mkdir("bar")
    qisrc_action.chdir("bar")
    foo_proj = qisrc_action("create", "foo")
    assert foo_proj.src == "bar/foo"

def test_slashes_in_argument(qisrc_action):
    qisrc_action.tmpdir.mkdir("bar")
    qisrc_action("create", "bar/baz")
    qisys.script.run_action("qibuild.actions.configure", ["baz"])

def test_template_path(qisrc_action, tmpdir):
    tmpl = tmpdir.mkdir("tmpl")
    tmpl.join("CMakeLists.txt").write("project(@ProjectName@)\n")
    qisrc_action("create", "HelloWorld", "--output", "helloworld",
                 "--template-path", tmpl.strpath)
    qisrc_action.reload_worktree()
    worktree = qisrc_action.git_worktree.worktree
    helloworld_proj = worktree.get_project("helloworld")
    with open(os.path.join(helloworld_proj.path, "CMakeLists.txt")) as fp:
        assert fp.read() == "project(HelloWorld)\n"