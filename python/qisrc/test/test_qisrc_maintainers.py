# -*- encoding: utf-8 -*-

## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisrc.maintainers

def test_no_project(qisrc_action):
    error = qisrc_action("maintainers", "--list", raises=True)
    assert "at least one project" in error

def test_no_maintainers_yet(qisrc_action, record_messages):
    foo = qisrc_action.worktree.create_project("foo")
    qisrc_action("maintainers", "--list", "--project", "foo")
    assert record_messages.find("No maintainer")

def test_add_cmdline(qisrc_action, record_messages):
    foo = qisrc_action.worktree.create_project("foo")
    qisrc_action("maintainers", "--add", "--project", "foo",
                 "--name", "John Smith", "--email", "jsmith@foo.corp")
    qisrc_action("maintainers", "--project", "foo")
    assert record_messages.find("John Smith")
    assert record_messages.find("<jsmith@foo.corp>")

def test_add_interact(qisrc_action, interact):
    foo = qisrc_action.worktree.create_project("foo")
    qisrc_action.chdir(foo.path)
    interact.answers = ["John Doe", "jdoe@example.com"]
    qisrc_action("maintainers", "--add")
    maintainers = qisrc.maintainers.get(foo)
    assert maintainers == [{"name" : "John Doe",
                            "email" : "jdoe@example.com"}]

def test_remove_maintainer(qisrc_action, interact):
    foo = qisrc_action.worktree.create_project("foo")
    qisrc.maintainers.add(foo, name="John Smith",
                          email="jsmith@foo.corp")
    interact.answers = [1]
    qisrc_action.chdir("foo")
    qisrc_action("maintainers", "--remove")
    assert not qisrc.maintainers.get(foo)

def test_add_utf8(qisrc_action):
    foo = qisrc_action.worktree.create_project("foo")
    qisrc.maintainers.add(foo, name="Noé", email="noe@ark.com")

def test_list_utf8(qisrc_action):
    foo = qisrc_action.worktree.create_project("foo")
    qisrc.maintainers.add(foo, name="Noé", email="noe@ark.com")
    qisrc_action("maintainers", "--list", "--project", "foo")
