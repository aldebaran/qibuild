## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.config
import qitoolchain.toolchain

def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    word_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo", word_package)
    qitoolchain_action("remove-package", "-c", "foo", "world")
    foo = qitoolchain.get_toolchain("foo")
    assert foo.packages == list()

def test_fails_when_no_such_package(qitoolchain_action):
    qitoolchain_action("create", "foo")
    qibuild.config.add_build_config("foo", toolchain="foo")
    error = qitoolchain_action("remove-package", "-c", "foo", "world", raises=True)
    assert "No such package" in error
