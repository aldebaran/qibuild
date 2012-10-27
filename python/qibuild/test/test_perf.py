## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import subprocess
import csv

import pytest

import qibuild
import qibuild.test
import qibuild.performance
from qibuild.test.test_toc import TestToc


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_cmake_parsing():
    with TestToc() as toc:
        proj = toc.get_project("perf")
        toc.configure_project(proj)
        toc.build_project(proj)
        test_path = os.path.join(proj.sdk_directory, "bin")
        res_path = os.path.join(proj.build_directory, 'perf-results/perf.xml')
        expected_tests = [
            ["perf_spam"],
            ["perf_eggs", "--foo", "bar"],
        ]
        actual_tests = qibuild.performance.parse_perflist_files(proj.build_directory)
        assert actual_tests == expected_tests

        # Check that re-running cmake does not create new tests:
        toc.configure_project(proj, clean_first=False)
        actual_tests = qibuild.performance.parse_perflist_files(proj.build_directory)
        assert actual_tests == expected_tests


# pylint: disable-msg=E1101
@pytest.mark.slow
def test_perf():
    with TestToc() as toc:
        proj = toc.get_project("perf")
        toc.configure_project(proj)
        toc.build_project(proj)
        qibuild.performance.run_perfs(proj)
        for name in ["perf_spam", "perf_eggs"]:
            expected_path = os.path.join(proj.build_directory, "perf-results", name + ".xml")
            assert os.path.exists(expected_path)
