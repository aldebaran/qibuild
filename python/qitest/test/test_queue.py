#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Queue """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import time

import qitest.runner
import qitest.result
import qitest.test_queue
from qisys import ui


class DummyProject(object):
    """ DummyProject """

    def __init__(self, tmpdir):
        """ DummyProject Init """
        self.sdk_directory = tmpdir.strpath


class DummyLauncher(qitest.runner.TestLauncher):
    """ DummyLauncher """

    def __init__(self, tmpdir):
        """ DummyLauncher Init """
        super(DummyLauncher, self).__init__()
        self.results = dict()
        self.project = DummyProject(tmpdir)

    def launch(self, test):
        """ Launch """
        default_time = 0.2
        default_result = qitest.result.TestResult(test)
        default_result.ok = True
        default_result.message = (ui.green, "[OK]")
        sleep_time = default_time
        result = default_result
        fate = self.results.get(test["name"])
        if fate:
            sleep_time = fate.get("sleep_time", default_time)
            result = fate.get("result", default_result)
            if fate.get('raises'):
                raise Exception("Kaboom!")
        time.sleep(sleep_time)
        return result


def test_queue_happy(tmpdir):
    """ Test Queue Happy """
    tests = [
        {"name": "one"},
        {"name": "two"},
        {"name": "three"},
        {"name": "four"},
        {"name": "five"},
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    dummy_launcher = DummyLauncher(tmpdir)
    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=3)
    assert test_queue.ok


def test_queue_sad(tmpdir):
    """ Test Queue Sad """
    tests = [
        {"name": "one"},
        {"name": "two"},
        {"name": "three"},
        {"name": "four"},
        {"name": "five"},
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    fail_result = qitest.result.TestResult(tests[1])
    fail_result.ok = False
    fail_result.message = (ui.red, "[FAIL]")
    dummy_launcher = DummyLauncher(tmpdir)
    dummy_launcher.results = {
        "two": {"result": fail_result},
        "three": {"raises": True},
        "four": {"sleep_time": 0.4},
    }
    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=3)
    assert not test_queue.ok


def test_one_job(tmpdir):
    """ Test One Job """
    tests = [
        {"name": "one"},
        {"name": "two"},
        {"name": "three"},
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    dummy_launcher = DummyLauncher(tmpdir)
    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=1)
    assert test_queue.ok


def test_no_tests(tmpdir):
    """ Test No Tests """
    tests = list()
    test_queue = qitest.test_queue.TestQueue(tests)
    dummy_launcher = DummyLauncher(tmpdir)
    test_queue.launcher = dummy_launcher
    test_queue.run(num_jobs=1)
    assert not test_queue.ok


class SporadicallyFailingLauncher(qitest.runner.TestLauncher):
    """ SporadicallyFailingLauncher """

    def __init__(self, tmpdir):
        """ SporadicallyFailingLauncher Init """
        super(SporadicallyFailingLauncher, self).__init__()
        self.num_runs = 0
        self.project = DummyProject(tmpdir)

    def launch(self, test):
        """ Launch """
        result = qitest.result.TestResult(test)
        if self.num_runs == 3:
            result.ok = False
            result.message = (ui.red, "[FAILED]")
        else:
            result.ok = True
            result.message = (ui.green, "[OK]")
        self.num_runs += 1
        return result


def test_repeat_until_fail(tmpdir):
    """ Test Repeat Until Fail """
    tests = [
        {"name": "one"},
        {"name": "two"}
    ]
    test_queue = qitest.test_queue.TestQueue(tests)
    fake_launcher = SporadicallyFailingLauncher(tmpdir)
    test_queue.launcher = fake_launcher
    test_queue.run(repeat_until_fail=3)
    assert test_queue.ok is False
