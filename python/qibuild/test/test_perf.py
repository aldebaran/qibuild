## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.sh
import qibuild.test
import qibuild.performance
from qibuild.test.test_toc import TestToc

def test_cmake_parsing():
    with TestToc() as toc:
        proj = toc.get_project("perf")
        toc.configure_project(proj)
        toc.build_project(proj)

        perf_spam = os.path.join(proj.sdk_directory, "bin/perf_spam")
        perf_eggs = os.path.join(proj.sdk_directory, "bin/perf_eggs")
        perf_timeout = os.path.join(proj.sdk_directory, "bin/perf_timeout")
        perf_segv = os.path.join(proj.sdk_directory, "bin/perf_segv")
        expected_tests = [
            ["perf_spam", qisys.sh.to_native_path(perf_spam), "42"],
            ["perf_eggs", qisys.sh.to_native_path(perf_eggs), "120", "--foo", "bar"],
            ["perf_timeout", qisys.sh.to_native_path(perf_timeout), "1"],
            ["perf_segv", qisys.sh.to_native_path(perf_segv), "120"]
        ]
        actual_tests = qibuild.performance.parse_perflist_files(
            proj.build_directory)
        assert len(actual_tests) == 4
        for (actual, expected) in zip(actual_tests, expected_tests):
            check_tests_are_equal(actual, expected)

        # Check that re-running cmake does not create new tests:
        toc.configure_project(proj, clean_first=False)
        actual_tests = qibuild.performance.parse_perflist_files(
                                           proj.build_directory)
        actual_tests = qibuild.performance.parse_perflist_files(
            proj.build_directory)
        for (actual, expected) in zip(actual_tests, expected_tests):
            check_tests_are_equal(actual, expected)


def test_perf():
    with TestToc() as toc:
        proj = toc.get_project("perf")
        toc.configure_project(proj)
        toc.build_project(proj)
        qibuild.performance.run_perfs(proj)
        for name in ["perf_spam", "perf_eggs"]:
            expected_path = os.path.join(proj.build_directory,
                "perf-results", name + ".xml")
            assert os.path.exists(expected_path)
        for name in ["perf_timeout", "perf_segv"]:
            expected_path = os.path.join(proj.build_directory,
                "perf-results", name + ".xml")
            assert not os.path.exists(expected_path)

def check_tests_are_equal(actual, expected):
    a_name, a_binary, a_timeout, a_args = \
    actual[0], actual[1], actual[2], actual[3:]
    b_name, b_binary, b_timeout, b_args = \
    expected[0], expected[1], expected[2], expected[3:]
    assert a_name == b_name
    if os.name != 'nt':
        # CMake stores some paths in short form (...~1), probably when reading them
        # from the registry, but python only uses long names
        #
        # Solution here does not work:
        # http://mail.python.org/pipermail/python-win32/2008-January/006642.html
        #
        # But anyway this is tested on linux and by the other test, so
        # don't bother to check that on Windows
        assert a_binary == b_binary
    assert a_timeout == b_timeout
    assert a_args == b_args
