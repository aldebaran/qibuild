import qitest.runner

import pytest


def test_match_patterns():
    test_foo = { "name" : "test_foo"}
    test_bar = { "name" : "test_bar"}
    test_foo_bar = { "name" : "test_foo_bar" }
    tests = [test_foo, test_bar, test_foo_bar]

    test_runner = qitest.runner.TestSuiteRunner(tests)

    test_runner.pattern = "foo"
    assert test_runner.tests == [test_foo, test_foo_bar]

    with pytest.raises(Exception):
        test_runner.pattern = "foo("

    test_runner.pattern = None
    assert test_runner.tests == [test_foo, test_bar, test_foo_bar]


def test_run(compiled_tests):
    test_runner = qitest.runner.TestSuiteRunner(compiled_tests)
    ok = test_runner.run()
    assert not ok


def test_no_perf_by_default():
    test_one = {"name" : "test_one"}
    perf_one = {"name" : "perf_one", "perf": True}
    test_two = {"name" : "test_two"}
    test_runner = qitest.runner.TestSuiteRunner(
        [test_one, perf_one, test_two]
    )
    test_runner.tests == [test_one, test_two]
