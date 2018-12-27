#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiTest Collect """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os

import qitest.conf
from qitest.test.conftest import qitest_action
from qibuild.test.conftest import record_messages


def test_simple(qitest_action, record_messages):
    """ Test Simple """
    testme_proj = qitest_action.add_test_project("testme")
    qitest_action("collect")
    pytest_json = os.path.join(testme_proj.path, "pytest.json")
    tests = qitest.conf.parse_tests(pytest_json)
    names = [x["name"] for x in tests]
    assert set(names) == set([
        "testme.test.test_foo",
        "testme.test.test_bar",
        "testme.test.subfolder.test_spam"])
