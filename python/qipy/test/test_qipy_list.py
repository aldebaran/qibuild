# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


def test_simple(qipy_action, record_messages):
    qipy_action.add_test_project("a_lib")
    qipy_action.add_test_project("big_project")
    qipy_action.add_test_project("foomodules")
    qipy_action("list")
    assert record_messages.find(r"\*\s+a")
    assert record_messages.find(r"\*\s+big_project")
