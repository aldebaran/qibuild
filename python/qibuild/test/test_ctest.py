## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest

from qibuild.ctest import parse_ctest_test_files


def test_parse_with_properties(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
# CMake generated Testfile ...
# ...
# ...

ADD_TEST(test_root "/path/to/test_root")
SET_TESTS_PROPERTIES(test_root PROPERTIES TIMEOUT "20" ENVIRONMENT "SPAM=EGGS")
SUBDIRS(a)
""")
    build_dir_a = build_dir.mkdir("a")
    build_dir_a.join("CTestTestfile.cmake").write("""
ADD_TEST(a_gtest "/path/to/a_gtest" "--gtest_output=xml:/path/to/a.xml")
SET_TESTS_PROPERTIES(a_gtest PROPERTIES TIMEOUT "20")
""")

    tests = parse_ctest_test_files(build_dir.strpath)
    expected = [
        ["test_root", ["/path/to/test_root"],
             {"ENVIRONMENT":"SPAM=EGGS", "TIMEOUT": "20"}],
        ["a_gtest", ["/path/to/a_gtest", "--gtest_output=xml:/path/to/a.xml"],
            {"TIMEOUT" : "20"}],
    ]

    assert tests == expected

def test_parse_no_properties(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
SUBDIRS(a)
ADD_TEST(test_root "/path/to/test_root")
""")
    build_dir_a = build_dir.mkdir("a")
    build_dir_a.join("CTestTestfile.cmake").write("""
ADD_TEST(a_gtest "/path/to/a_gtest" "--gtest_output=xml:/path/to/a.xml")
""")

    tests = parse_ctest_test_files(build_dir.strpath)
    expected = [
        ["test_root", ["/path/to/test_root"], {}],
        ["a_gtest", ["/path/to/a_gtest", "--gtest_output=xml:/path/to/a.xml"], {}],
    ]
    assert tests == expected


def test_parse_mix_properties(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
SUBDIRS(a)
ADD_TEST(test_root "/path/to/test_root")
""")
    build_dir_a = build_dir.mkdir("a")
    build_dir_a.join("CTestTestfile.cmake").write("""
ADD_TEST(a_gtest "/path/to/a_gtest" "--gtest_output=xml:/path/to/a.xml")
SET_TESTS_PROPERTIES(a_gtest PROPERTIES TIMEOUT "20")
""")

    tests = parse_ctest_test_files(build_dir.strpath)
    expected = [
        ["test_root", ["/path/to/test_root"], {}],
        ["a_gtest", ["/path/to/a_gtest", "--gtest_output=xml:/path/to/a.xml"],
            {"TIMEOUT" : "20"} ]
    ]
    assert tests == expected

def test_strange_names(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
ADD_TEST(test-FooBar_2 "/path/to/test_root")
SET_TESTS_PROPERTIES(test-FooBar_2 PROPERTIES TIMEOUT "20")
""")
    tests = list()
    subdirs = list()
    tests = parse_ctest_test_files(build_dir.strpath)
    expected = [
        ["test-FooBar_2", ["/path/to/test_root"], {"TIMEOUT" : "20"}]
    ]
    assert tests == expected

def test_set_test_with_no_add_test(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
SET_TESTS_PROPERTIES(a_gtest PROPERTIES TIMEOUT "20")
""")

    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_ctest_test_files(build_dir.strpath)
    assert "Expecting ADD_TEST before SET_TESTS_PROPERTIES" in str(e)


def test_set_wrong_name(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
ADD_TEST(test_root "/path/to/test_root")
SET_TESTS_PROPERTIES(a_gtest PROPERTIES TIMEOUT "20")
""")

    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        parse_ctest_test_files(build_dir.strpath)
    assert "SET_TESTS_PROPERTIES called with wrong name" in str(e)

def test_set_properties_called_twice_same_key(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
ADD_TEST(test_root "/path/to/test_root")
SET_TESTS_PROPERTIES(test_root PROPERTIES TIMEOUT "20")
SET_TESTS_PROPERTIES(test_root PROPERTIES TIMEOUT "200")
""")
    with pytest.raises(Exception) as e:
        parse_ctest_test_files(build_dir.strpath)
    assert "Expecting ADD_TEST before SET_TESTS_PROPERTIES" in str(e)


def test_set_properties_called_twice_different_keys(tmpdir):
    build_dir = tmpdir.mkdir("build")
    build_dir.join("CTestTestfile.cmake").write("""
ADD_TEST(test_root "/path/to/test_root")
SET_TESTS_PROPERTIES(test_root PROPERTIES TIMEOUT "20")
SET_TESTS_PROPERTIES(test_root PROPERTIES BAR BAZ)
""")
    with pytest.raises(Exception) as e:
        parse_ctest_test_files(build_dir.strpath)
    assert "Expecting ADD_TEST before SET_TESTS_PROPERTIES" in str(e)
