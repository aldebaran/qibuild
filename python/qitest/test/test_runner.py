## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qitest.project
import qitest.runner

import pytest

class DummyTestRunner(qitest.runner.TestSuiteRunner):
    def launcher(self, *args):
        pass

def test_match_patterns(tmpdir):
    test_foo = { "name" : "test_foo"}
    test_bar = { "name" : "test_bar"}
    test_foo_bar = { "name" : "test_foo_bar" }
    test_spam = { "name" : "test_spam" }
    nightly = { "name" : "nightly", "nightly" : True}
    perf = { "name" : "perf", "perf" : True}
    tests = [test_foo, test_bar, test_foo_bar, test_spam, nightly, perf]
    qitest_json = tmpdir.ensure("qitest.json", file=True)
    qitest.conf.write_tests(tests, qitest_json.strpath)
    test_project = qitest.project.TestProject(qitest_json.strpath)
    test_runner = DummyTestRunner(test_project)

    test_runner.patterns = ["foo"]
    assert test_runner.tests == [test_foo, test_foo_bar]

    test_runner.patterns = ["foo", "bar"]
    assert test_runner.tests == [test_foo, test_bar, test_foo_bar]

    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        test_runner.patterns = "foo("

    test_runner.patterns = list()
    assert test_runner.tests == [test_foo, test_bar, test_foo_bar, test_spam]

    test_runner.nightly = True
    test_runner.perf = False
    assert test_runner.tests == [test_foo, test_bar, test_foo_bar, test_spam, nightly]

    test_runner.perf = True
    test_runner.nightly = False
    assert test_runner.tests == [perf]

def test_exclude(tmpdir):
    test_foo = { "name" : "test_foo"}
    test_bar = { "name" : "test_bar"}
    test_foo_bar = { "name" : "test_foo_bar" }

    tests = [test_foo, test_bar, test_foo_bar]
    qitest_json = tmpdir.ensure("qitest.json", file=True)
    qitest.conf.write_tests(tests, qitest_json.strpath)
    test_project = qitest.project.TestProject(qitest_json.strpath)
    test_runner = DummyTestRunner(test_project)

    test_runner.excludes = ["foo"]
    assert test_runner.tests == [test_bar]
