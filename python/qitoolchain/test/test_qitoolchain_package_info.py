## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def test_simple(qitoolchain_action, toolchains, record_messages):
    toolchains.create("foo")
    toolchains.add_package("foo", "boost", package_version="1.57-r3")
    qitoolchain_action("package-info", "--toolchain", "foo", "boost")
    assert record_messages.find("boost 1.57-r3")
