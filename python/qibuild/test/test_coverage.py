#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Test Coverage.
Automatic testing for qibuild with coverage option.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qisys.command
import qibuild.test
import qibuild.gcov


def test_generate_reports(qibuild_action):
    """ Test Generate Reports """
    gcovr = qisys.command.find_program("gcovr", raises=False)
    if not gcovr:
        return
    proj = qibuild_action.add_test_project("cov")
    qibuild_action("configure", "cov", "--coverage")
    qibuild_action("make", "cov")
    qibuild.gcov.generate_coverage_reports(proj)
    expected_path_xml = os.path.join(proj.sdk_directory, "coverage-results", proj.name + ".xml")
    expected_path_html = os.path.join(proj.sdk_directory, "coverage-results", proj.name + ".html")
    assert os.path.exists(expected_path_xml)
    assert os.path.exists(expected_path_html)
    qibuild.gcov.generate_coverage_reports(proj, output_dir=proj.path)
    expected_path_xml = os.path.join(proj.path, proj.name + ".xml")
    expected_path_html = os.path.join(proj.path, proj.name + ".html")
    assert os.path.exists(expected_path_xml)
    assert os.path.exists(expected_path_html)
