#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test QiTest List """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import json
from qitest.test.conftest import qitest_action
from qibuild.test.conftest import record_messages


def test_simple(qitest_action, tmpdir, record_messages):
    """ Test Simple """
    tests = [
        {"name": "foo", "gtest": True},
        {"name": "test_bar"},
        {"name": "test_baz", "pytest": True}
    ]
    qitest_json = tmpdir.join("qitest.json")
    qitest_json.write(json.dumps(tests))
    qitest_action("list", cwd=tmpdir.strpath)
    assert record_messages.find(r"foo.*\(invalid name\)")
    assert record_messages.find(r"test_bar.*\(no type\)")
