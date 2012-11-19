## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
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
                       'COST' : '42.0',
                       'WORKING_DIRECTORY' : "a/work/dir"
                     }
        ],
        ['test_bar', ['/path/to/test_bar'],
                     {
                        'COST' : '53.2'
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

def test_verbosity(tmpdir, capsys):
    test = TestResult("test", 0, 1, verbose=True)
    test.ok = False
    test.print_result()
    out, err = capsys.readouterr()
    assert "no output" in out

    test2 = TestResult("test", 0, 1, verbose=True)
    test2.ok = False
    test2.out = "on output"
    test2.print_result()
    out, err = capsys.readouterr()
    assert "on output" in out

    test3 = TestResult("test", 0, 1, verbose=False)
    test3.ok = False
    test3.out = "output"
    test3.print_result()
    out, err = capsys.readouterr()
    assert "output" not in out
