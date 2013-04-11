## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest
from qibuild.ctest import parse_ctest_test_files
from qibuild.ctest import TestResult


def test_parse_simple(tmpdir):
    root_ctest = tmpdir.join("CTestTestfile.cmake")
    root_ctest.write("""
SUBDIRS(bar)
ADD_TEST(test_foo /path/to/test_foo --spam=eggs)
SET_TESTS_PROPERTIES(test_foo PROPERTIES COST 42.0 WORKING_DIRECTORY "a/work/dir")
""")
    bar = tmpdir.mkdir("bar")
    bar_ctest = bar.join("CTestTestfile.cmake")
    bar_ctest.write("""
ADD_TEST(test_bar "/path/to/test_bar")
SET_TESTS_PROPERTIES(test_bar PROPERTIES COST 53.2)
""")
    tests = parse_ctest_test_files(tmpdir.strpath)
    assert tests == [
        ['test_foo', ['/path/to/test_foo', '--spam=eggs'],
                     {
                       'COST': '42.0',
                       'WORKING_DIRECTORY': "a/work/dir"
                     }
        ],
        ['test_bar', ['/path/to/test_bar'],
                     {
                        'COST': '53.2'
                    }
        ]
    ]


def test_errors(tmpdir):
    root_ctest = tmpdir.join("CTestTestfile.cmake")
    root_ctest.write("""
SET_TESTS_PROPERTIES(foo PROPERTIES SPAM EGGS)
""")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_ctest_test_files(tmpdir.strpath)
    assert "Expecting ADD_TEST before SET_TESTS_PROPERTIES" in e.value.message

    root_ctest.write("""
ADD_TEST(foo /path/to/foo)
SET_TESTS_PROPERTIES(bar PROPERTIES SPAM EGGS)
""")
    with pytest.raises(Exception) as e:
        parse_ctest_test_files(tmpdir.strpath)
    assert "SET_TESTS_PROPERTIES called with wrong name" in e.value.message


# pylint: disable-msg=E1101
@pytest.mark.skipif('"dead locks"')
def test_failing_output_tests_always_printed(capsys):
    test1 = TestResult("test", 0, 2, verbose=False)
    test2 = TestResult("test", 1, 2, verbose=False)
    test1.ok = True
    test1.out = "test1"
    test2.ok = False
    test2.out = "test2"
    test1.print_result()
    test2.print_result()
    out, err = capsys.readouterr()
    assert "test1" not in out
    assert "test2" in out


# pylint: disable-msg=E1101
@pytest.mark.skipif('"dead locks"')
def test_passing_test_printed_when_verbose(capsys):
    test1 = TestResult("test", 0, 2, verbose=True)
    test2 = TestResult("test", 1, 2, verbose=True)
    test1.ok = True
    test1.out = "test1"
    test2.ok = False
    test2.out = "test2"
    test1.print_result()
    test2.print_result()
    out, err = capsys.readouterr()
    assert "test1" in out
    assert "test2" in out
