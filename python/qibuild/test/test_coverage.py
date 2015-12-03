## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for qibuild with coverage option

"""

import os

import qisys.command
import qibuild.test
import qibuild.gcov


def test_generate_reports(qibuild_action):
    gcovr = qisys.command.find_program("gcovr", raises=False)
    if not gcovr:
        return
    proj = qibuild_action.add_test_project("cov")
    qibuild_action("configure", "cov", "--coverage")
    qibuild_action("make", "cov")
    qibuild.gcov.generate_coverage_reports(proj)
    expected_path_xml = os.path.join(proj.build_directory, proj.name + ".xml")
    expected_path_html = os.path.join(proj.build_directory, proj.name + ".html")
    assert os.path.exists(expected_path_xml)
    assert os.path.exists(expected_path_html)

