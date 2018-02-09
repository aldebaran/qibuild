# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import qibuild.config

# pylint: disable=unused-variable


def test_simple(qitoolchain_action, record_messages):
    foo_tc = qitoolchain_action("create", "foo")
    bar_tc = qitoolchain_action("create", "bar")
    qibuild.config.add_build_config("foo", toolchain="foo")
    world_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", world_package)
    record_messages.reset()
    qitoolchain_action("info")
    assert record_messages.find("foo")
    assert record_messages.find("world")
    assert record_messages.find("bar")
    record_messages.reset()
    qitoolchain_action("info", "foo")
    assert record_messages.find("foo")
    assert record_messages.find("world")
    assert not record_messages.find("bar")
