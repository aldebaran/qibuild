import qitest.project
import qitest.runner

import pytest


def test_match_patterns(tmpdir):
    test_foo = { "name" : "test_foo"}
    test_bar = { "name" : "test_bar"}
    test_foo_bar = { "name" : "test_foo_bar" }
    nightly = { "name" : "nightly", "nightly" : True}
    perf = { "name" : "perf", "perf" : True}
    tests = [test_foo, test_bar, test_foo_bar, nightly, perf]
    qitest_json = tmpdir.ensure("qitest.json", file=True)
    qitest.conf.write_tests(tests, qitest_json.strpath)
    test_project = qitest.project.TestProject(qitest_json.strpath)
    test_runner = qitest.runner.TestSuiteRunner(test_project)

    test_runner.pattern = "foo"
    assert test_runner.tests == [test_foo, test_foo_bar]

    with pytest.raises(Exception):
        test_runner.pattern = "foo("

    test_runner.pattern = None
    assert test_runner.tests == [test_foo, test_bar, test_foo_bar]

    test_runner.nightly = True
    test_runner.perf = False
    assert test_runner.tests == [test_foo, test_bar, test_foo_bar, nightly]

    test_runner.perf = True
    test_runner.nightly = False
    assert test_runner.tests == [perf]
