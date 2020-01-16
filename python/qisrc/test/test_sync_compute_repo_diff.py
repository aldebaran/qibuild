#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Sync Compute Repo Diff """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.sync
import qisrc.manifest
import qisrc.git_config


def make_repos(*args):
    """ Make Repos """
    res = list()
    for arg in args:
        if len(arg) == 3:
            project_name, src, remote_names = arg
            default_branch = "master"
        if len(arg) == 4:
            project_name, src, remote_names, default_branch = arg
        repo = qisrc.manifest.RepoConfig()
        for remote_name in remote_names:
            remote = qisrc.git_config.Remote()
            if remote_name == "gerrit":
                remote.review = True
            remote.name = remote_name
            remote.url = "git://%s/%s" % (remote_name, project_name)
            repo.remotes.append(remote)
        repo.project = project_name
        repo.src = src
        repo.default_branch = default_branch
        res.append(repo)
    return res


def test_no_diff():
    """ Test No Diff """
    old = make_repos(
        ("foo.git", "foo", ["origin"]),
        ("bar.git", "bar", ["origin"])
    )
    new = make_repos(
        ("foo.git", "foo", ["origin"]),
        ("bar.git", "bar", ["origin"])
    )
    (to_add, to_move, to_rm, to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert to_move == list()
    assert to_rm == list()
    assert to_update == list()


def test_adding_a_remote():
    """ Test Adding a Remote """
    old = make_repos(
        ("foo.git", "foo", ["origin"]),
    )
    new = make_repos(
        ("foo.git", "foo", ["origin", "gerrit"])
    )
    (to_add, to_move, to_rm, to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert to_move == list()
    assert to_rm == list()
    assert len(to_update) == 1


def test_change_branch():
    """ Test Change Branch """
    old = make_repos(
        ("foo.git", "foo", ["origin"], "master"),
        ("bar.git", "bar", ["origin"], "master"),

    )
    new = make_repos(
        ("foo.git", "foo", ["origin"], "devel"),
        ("bar.git", "bar", ["origin"], "master"),
    )
    (to_add, to_move, to_rm, to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert to_move == list()
    assert to_rm == list()
    assert len(to_update) == 1
    (foo_old, foo_new) = to_update[0]
    assert foo_old.default_branch == "master"
    assert foo_new.default_branch == "devel"


def test_moving():
    """ Test Moving """
    old = make_repos(
        ("foo.git", "foo", ["origin"]),
        ("bar.git", "bar", ["origin", "gerrit"])
    )
    new = make_repos(
        ("bar.git", "bar", ["origin", "gerrit"]),
        ("foo.git", "lib/foo", ["origin"])
    )
    (to_add, to_move, to_rm, to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert len(to_move) == 1
    assert to_move[0][0].project == "foo.git"
    assert to_move[0][1] == "lib/foo"
    assert to_rm == list()
    assert to_update == list()


def test_rm_add():
    """ Test Rm Add """
    old = make_repos(
        ("foo.git", "foo", ["origin"]),
        ("bar.git", "bar", ["origin"]),
    )
    new = make_repos(
        ("foo.git", "foo", ["origin"]),
        ("spam.git", "spam", ["origin"]),
    )
    (to_add, to_move, to_rm, to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert len(to_add) == 1
    assert to_add[0].project == "spam.git"
    assert to_move == list()
    assert len(to_rm) == 1
    assert to_rm[0].project == "bar.git"
    assert to_update == list()


def test_changing_remote_url():
    """ Test Changing Remote Url """
    old = make_repos(
        ("git/foo.git", "foo", ["origin"]),
        ("bar.git", "bar", ["origin"]),
    )
    new = make_repos(
        ("gerrit/foo.git", "foo", ["origin"]),
        ("bar.git", "bar", ["origin"]),
    )
    (to_add, to_move, to_rm, to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add == list()
    assert to_rm == list()
    assert to_move == list()
    assert len(to_update) == 1
    assert to_update[0] == (old[0], new[0])


def test_evil_nested():
    """ Test Evil Nested """
    old = make_repos()
    new = make_repos(
        ("foo/bar.git", "foo/bar", ["origin"]),
        ("foo.git", "foo", ["origin"]),
    )
    (to_add, _to_move, _to_rm, _to_update) = qisrc.sync.compute_repo_diff(old, new)
    assert to_add[0].src == "foo"
    assert to_add[1].src == "foo/bar"
