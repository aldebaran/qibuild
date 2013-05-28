## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qibuild.test
import qibuild.performance
import qibuild.find

def test_cmake_parsing(qibuild_action):
    proj = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf")
    qibuild_action("make", "perf")
    perf_spam = qibuild.find.find_bin([proj.sdk_directory], "perf_spam", expect_one=True)
    perf_eggs = qibuild.find.find_bin([proj.sdk_directory], "perf_eggs", expect_one=True)
    expected_tests = [
        ["perf_spam", perf_spam],
        ["perf_eggs", perf_eggs, "--foo", "bar"],
    ]
    actual_tests = qibuild.performance.parse_perflist_files(
        proj.build_directory)
    assert actual_tests == expected_tests

    # Check that re-running cmake does not create new tests:
    proj.configure(clean_first=False)
    actual_tests = qibuild.performance.parse_perflist_files(
        proj.build_directory)
    assert actual_tests == expected_tests


def test_perf(qibuild_action):
    proj = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf")
    qibuild_action("make", "perf")
    qibuild.performance.run_perfs(proj)
    for name in ["perf_spam", "perf_eggs"]:
        expected_path = os.path.join(proj.build_directory,
            "perf-results", name + ".xml")
        assert os.path.exists(expected_path)
