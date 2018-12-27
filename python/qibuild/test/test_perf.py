#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Perf """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os


def test_perf(qibuild_action):
    """ Test Perf """
    proj = qibuild_action.add_test_project("perf")
    qibuild_action("configure", "perf", "-DQI_WITH_PERF_TESTS=ON")
    qibuild_action("make", "perf")
    proj.run_tests(perf=True)
    for name in ["perf_spam", "perf_eggs"]:
        expected_path = os.path.join(proj.sdk_directory,
                                     "perf-results", name + ".xml")
        assert os.path.exists(expected_path)
    for name in ["perf_timeout", "perf_segv"]:
        expected_path = os.path.join(proj.sdk_directory,
                                     "perf-results", name + ".xml")
        assert not os.path.exists(expected_path)
