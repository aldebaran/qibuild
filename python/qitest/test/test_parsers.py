#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Parsers """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qitest.parsers
from qibuild.test.conftest import TestBuildWorkTree, args, build_worktree, qibuild_action


def test_nothing_specified_json_in_cwd(args, tmpdir, monkeypatch):
    """ Test Nothing Specified JSON in cwd """
    monkeypatch.chdir(tmpdir)
    qitest_json = tmpdir.ensure("qitest.json")
    qitest_json.write("[]")
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.project.sdk_directory == tmpdir.strpath


def test_nothing_specified_inside_qibuild_project(args, build_worktree, monkeypatch):
    """ Test Nothing Specified Inside QiBuild Project """
    world_proj = build_worktree.add_test_project("world")
    world_proj.configure()
    monkeypatch.chdir(world_proj.path)
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.project.sdk_directory == world_proj.sdk_directory


def test_non_empty_working_dir(args, tmpdir, monkeypatch):
    """ Test Non Empty Working Dir """
    monkeypatch.chdir(tmpdir)
    qitest_json = tmpdir.ensure("qitest.json")
    args.qitest_json = "qitest.json"
    qitest_json.write("[]")
    test_runner = qitest.parsers.get_test_runner(args)
    assert test_runner.cwd == tmpdir


def test_specifying_qitest_json(args, tmpdir):
    """ Test Specifying QiTest JSON """
    qitest_json = tmpdir.ensure("qitest.json")
    qitest_json.write("[]")
    args.qitest_json = qitest_json.strpath
    test_runner = qitest.parsers.get_test_runner(args)
    assert test_runner.project.sdk_directory == tmpdir.strpath


def test_bad_qibuild_config_with_qitest_json(args, qibuild_action, monkeypatch):
    """ Test Bad QiBuild Config With QiTest JSON """
    qibuild_action.add_test_project("testme")
    qibuild_action("add-config", "foo")
    qibuild_action("configure", "--config", "foo", "testme")
    build_worktree = TestBuildWorkTree()
    build_worktree.set_active_config("foo")
    testme_proj = build_worktree.get_build_project("testme")
    testme_sdk = testme_proj.sdk_directory
    qitest_json = os.path.join(testme_sdk, "qitest.json")
    monkeypatch.chdir(testme_proj.path)
    args.qitest_jsons = [qitest_json]
    _test_runners = qitest.parsers.get_test_runners(args)


def test_several_qibuild_projects(args, build_worktree, monkeypatch):
    """ Test Several QiBuild Projects """
    world_proj = build_worktree.add_test_project("world")
    test_proj = build_worktree.add_test_project("testme")
    world_proj.configure()
    test_proj.configure()
    monkeypatch.chdir(build_worktree.root)
    args.projects = ["world", "testme"]
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2
    world_runner, testme_runner = test_runners
    assert world_runner.project.sdk_directory == world_proj.sdk_directory
    assert testme_runner.project.sdk_directory == test_proj.sdk_directory


def test_using_dash_all(args, build_worktree, monkeypatch):
    """ Test Usin Dash All """
    world_proj = build_worktree.create_project("world")
    hello_proj = build_worktree.create_project("hello")
    world_proj.configure()
    hello_proj.configure()
    args.all = True
    monkeypatch.chdir(build_worktree.root)
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2


def test_several_qitest_json(args, tmpdir, monkeypatch):
    """ Test Several QiTest JSON """
    monkeypatch.chdir(tmpdir)
    json1 = tmpdir.join("1.json")
    json1.write("[]")
    json2 = tmpdir.join("2.json")
    json2.write("[]")
    args.qitest_jsons = [json1.strpath, json2.strpath]
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2


def test_qitest_json_from_worktree(args, build_worktree, monkeypatch):
    """ Test QiTest JSON From WorkTree """
    testme_proj = build_worktree.add_test_project("testme")
    testme_proj.configure()
    monkeypatch.chdir(testme_proj.path)
    qitest_json = os.path.join(testme_proj.sdk_directory, "qitest.json")
    args.qitest_jsons = [qitest_json]
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.cwd == testme_proj.sdk_directory


def test_nothing_to_test(args, cd_to_tmpdir):
    """ Test Nothing To Test """
    with pytest.raises(Exception) as e:
        qitest.parsers.get_test_runners(args)
    assert e.value.message == "Nothing found to test"


def test_coverage_in_build_worktree(args, build_worktree, monkeypatch):
    """ Test Coverage In Build WorkTree """
    world_proj = build_worktree.create_project("world")
    world_proj.configure()
    monkeypatch.chdir(world_proj.path)
    args.coverage = True
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.cwd == world_proj.sdk_directory
    assert test_runner.coverage


def test_ignore_timeouts(args, tmpdir, monkeypatch):
    """ Test ngnore TimeOuts """
    monkeypatch.chdir(tmpdir)
    tmpdir.join("qitest.json").write("[]")
    args.ignore_timeouts = True
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.ignore_timeouts
