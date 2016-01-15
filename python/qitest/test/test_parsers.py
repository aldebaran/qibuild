## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os

import pytest

import qisys.error
import qitest.parsers

from qibuild.test.conftest import TestBuildWorkTree

def test_nothing_specified_json_in_cwd(args, tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    qitest_json = tmpdir.ensure("qitest.json")
    qitest_json.write("[]")
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.project.sdk_directory == tmpdir.strpath

def test_nothing_specified_inside_qibuild_project(args, build_worktree, monkeypatch):
    world_proj = build_worktree.add_test_project("world")
    world_proj.configure()
    monkeypatch.chdir(world_proj.path)
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.project.sdk_directory == world_proj.sdk_directory

def test_non_empty_working_dir(args, tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    qitest_json = tmpdir.ensure("qitest.json")
    args.qitest_json = "qitest.json"
    qitest_json.write("[]")
    test_runner = qitest.parsers.get_test_runner(args)
    assert test_runner.cwd == tmpdir

def test_specifying_qitest_json(args, tmpdir):
    qitest_json = tmpdir.ensure("qitest.json")
    qitest_json.write("[]")
    args.qitest_json = qitest_json.strpath
    test_runner = qitest.parsers.get_test_runner(args)
    assert test_runner.project.sdk_directory == tmpdir.strpath

def test_bad_qibuild_config_with_qitest_json(args, qibuild_action, monkeypatch):
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
    test_runners = qitest.parsers.get_test_runners(args)

def test_several_qibuild_projects(args, build_worktree, monkeypatch):
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
    world_proj = build_worktree.create_project("world")
    hello_proj = build_worktree.create_project("hello")
    world_proj.configure()
    hello_proj.configure()
    args.all = True
    monkeypatch.chdir(build_worktree.root)
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2

def test_several_qitest_json(args, tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    json1 = tmpdir.join("1.json")
    json1.write("[]")
    json2 = tmpdir.join("2.json")
    json2.write("[]")
    args.qitest_jsons = [json1.strpath, json2.strpath]
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 2

def test_qitest_json_from_worktree(args, build_worktree, monkeypatch):
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
    # pylint:disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qitest.parsers.get_test_runners(args)
    assert e.value.message == "Nothing found to test"

def test_coverage_in_build_worktree(args, build_worktree, monkeypatch):
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
    monkeypatch.chdir(tmpdir)
    tmpdir.join("qitest.json").write("[]")
    args.ignore_timeouts = True
    test_runners = qitest.parsers.get_test_runners(args)
    assert len(test_runners) == 1
    test_runner = test_runners[0]
    assert test_runner.ignore_timeouts
