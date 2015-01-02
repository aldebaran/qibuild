## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qitoolchain

def test_simple(qitoolchain_action):
    qitoolchain_action("create", "foo")
    word_package = qitoolchain_action.get_test_package("world")
    qitoolchain_action("add-package", "-c", "foo",  word_package)
    tc = qitoolchain.get_toolchain("foo")
    world_package = tc.packages[0]
    assert world_package.name == "world"
    assert world_package.path
