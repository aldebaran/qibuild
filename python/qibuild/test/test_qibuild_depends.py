# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


def test_simple(qibuild_action, record_messages):  # pylint: disable=unused-argument
    # More complex tests should be written at a lower level
    qibuild_action.create_project("world")
    qibuild_action.create_project("hello", build_depends=["world"])
    qibuild_action("depends", "hello")
