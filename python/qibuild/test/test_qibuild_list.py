## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
def test_simple(qibuild_action, record_messages):
    qibuild_action.add_test_project("world")
    qibuild_action("list")
    assert record_messages.find("world")

def test_empty(qibuild_action, record_messages):
    qibuild_action("list")
    assert record_messages.find("Please use")
