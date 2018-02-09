# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os

import qitest.conf


def test_simple(qitest_action, record_messages):  # pylint: disable=unused-argument
    testme_proj = qitest_action.add_test_project("testme")
    qitest_action("collect")
    pytest_json = os.path.join(testme_proj.path, "pytest.json")
    tests = qitest.conf.parse_tests(pytest_json)
    names = [x["name"] for x in tests]
    assert set(names) == set([
        "testme.test.test_foo",
        "testme.test.test_bar",
        "testme.test.subfolder.test_spam"])
