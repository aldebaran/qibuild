#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test SVN """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.svn


def test_commit_all_adds_new_subfolders(svn_server, tmpdir):
    """ Test Commit All Adds New SubFolders """
    foo_url = svn_server.create_repo("foo")
    work = tmpdir.mkdir("work")
    foo1 = work.mkdir("foo")
    svn = qisrc.svn.Svn(foo1.strpath)
    svn.call("checkout", foo_url, ".")
    foo1.ensure("some/sub/folder", dir=True)
    foo1.ensure("some/sub/folder/bar.txt")
    svn.commit_all("test message")
    work2 = tmpdir.mkdir("work2")
    foo2 = work2.mkdir("foo2")
    svn = qisrc.svn.Svn(foo2.strpath)
    svn.call("checkout", foo_url, ".")
    assert foo2.join("some", "sub", "folder").check(dir=True)
    assert foo2.join("some", "sub", "folder", "bar.txt").check(file=True)


def test_commit_all_removes_removed_files(svn_server, tmpdir):
    """ Test Commit All Removes Removed Files """
    foo_url = svn_server.create_repo("foo")
    svn_server.commit_file("foo", "bar.txt", "this is bar")
    work = tmpdir.mkdir("work")
    foo1 = work.mkdir("foo")
    svn = qisrc.svn.Svn(foo1.strpath)
    svn.call("checkout", foo_url, ".")
    foo1.join("bar.txt").remove()
    svn.commit_all("test message")
    work2 = tmpdir.mkdir("work2")
    foo2 = work2.mkdir("foo2")
    svn = qisrc.svn.Svn(foo2.strpath)
    svn.call("checkout", foo_url, ".")
    assert not foo2.join("bar.txt").check(file=True)


def test_files_with_space(svn_server, tmpdir):
    """ Test Files With Space """
    foo_url = svn_server.create_repo("foo")
    svn_server.commit_file("foo", "file with space.txt", "some contents\n")
    work = tmpdir.mkdir("work")
    foo1 = work.mkdir("foo")
    svn = qisrc.svn.Svn(foo1.strpath)
    svn.call("checkout", foo_url, ".")
    foo1.join("file with space.txt").remove()
    svn.commit_all("test message")


def test_file_replaced_by_symlink(svn_server, tmpdir):
    """ Test File Replaced By Simlink """
    foo_url = svn_server.create_repo("foo")
    svn_server.commit_file("foo", "a.txt", "this is a\n")
    work = tmpdir.mkdir("work")
    foo1 = work.mkdir("foo")
    svn = qisrc.svn.Svn(foo1.strpath)
    svn.call("checkout", foo_url, ".")
    foo1.join("a.txt").remove()
    foo1.ensure("b.txt", file=True)
    foo1.join("a.txt").mksymlinkto("b.txt")
    svn.commit_all("test message")
