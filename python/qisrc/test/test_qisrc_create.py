#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiSrc Create """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qisrc.git
import qisys.script
from qisys.test.conftest import TestWorkTree


def test_simple(qisrc_action):
    """ Test Simple """
    qisrc_action("create", "foo")
    # cannot use qibuild_action fixture without creating recursive
    # dependencies ...
    qisys.script.run_action("qibuild.actions.configure", ["foo"])


def test_with_git(qisrc_action):
    """ Test With Git """
    qisrc_action("create", "foo", "--git")
    worktree = TestWorkTree()
    foo_proj = worktree.get_project("foo")
    git = qisrc.git.Git(foo_proj.path)
    ret, out = git.call("show", "HEAD", raises=False)
    assert ret == 0
    assert ".gitignore" in out


def test_in_subdir(qisrc_action):
    """ Test In SubDir """
    qisrc_action.tmpdir.mkdir("bar")
    qisrc_action.chdir("bar")
    foo_proj = qisrc_action("create", "foo")
    assert foo_proj.src == "bar/foo"


def test_slashes_in_argument(qisrc_action):
    """ Test Slashes in Argument """
    qisrc_action.tmpdir.mkdir("bar")
    qisrc_action("create", "bar/baz")
    qisys.script.run_action("qibuild.actions.configure", ["baz"])


def test_template_path(qisrc_action, tmpdir):
    """ Test Template Path """
    tmpl = tmpdir.mkdir("tmpl")
    tmpl.join("CMakeLists.txt").write("project(@ProjectName@)\n")
    qisrc_action("create", "HelloWorld", "--output", "helloworld",
                 "--template-path", tmpl.strpath)
    qisrc_action.reload_worktree()
    worktree = qisrc_action.git_worktree.worktree
    helloworld_proj = worktree.get_project("helloworld")
    with open(os.path.join(helloworld_proj.path, "CMakeLists.txt")) as fp:
        assert fp.read() == "project(HelloWorld)\n"


def test_domain(qisrc_action, tmpdir):
    """ Test Domain """
    tmpl = tmpdir.mkdir("tmpl")
    tmpl.join("CMakeLists.txt").write("project(@ProjectName@)\n@domain@")
    qisrc_action("create", "HelloWorld", "--params", "domain=aldebaran.com", "--output", "helloworld",
                 "--template-path", tmpl.strpath)
    qisrc_action.reload_worktree()
    worktree = qisrc_action.git_worktree.worktree
    helloworld_proj = worktree.get_project("helloworld")
    with open(os.path.join(helloworld_proj.path, "CMakeLists.txt")) as fp:
        assert fp.read() == "project(HelloWorld)\naldebaran.com"


def test_no_worktree(tmpdir):
    """ Test No WorkTree """
    tmpl = tmpdir.mkdir("tmpl")
    tmpl.join("@project_name@.txt").write("")
    dest = tmpdir.mkdir("dest")
    with qisys.sh.change_cwd(dest.strpath):
        qisys.script.run_action("qisrc.actions.create",
                                ["--template-path", tmpl.strpath, "HelloWorld"])
    assert dest.join("helloworld", "hello_world.txt").check(file=True)


def test_create_inside_template(tmpdir):
    """ Test Create Inside Template """
    tmpl = tmpdir.mkdir("tmpl")
    tmpl.join("@project_name@.txt").write("")
    inside = tmpl.mkdir("dest")
    with qisys.sh.change_cwd(inside.strpath):
        with pytest.raises(Exception) as e:
            qisys.script.run_action("qisrc.actions.create",
                                    ["--template-path", tmpl.strpath, "HelloWorld"])
        assert e.value.message == "output directory is inside input directory"
