# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


def test_simple(qidoc_action, record_messages):
    qidoc_action.add_test_project("world")
    qidoc_action.add_test_project("libworld")
    qidoc_action("list")
    assert record_messages.find(r"\*\s+world")
    assert record_messages.find(r"\*\s+libworld")
