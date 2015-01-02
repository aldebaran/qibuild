## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qitoolchain.toolchain

import pytest

def test_simple(qitoolchain_action):
    qitoolchain.toolchain.Toolchain("foo")
    qitoolchain_action("remove", "-f", "foo")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qitoolchain.get_toolchain("foo")

def test_when_not_exists(qitoolchain_action):
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qitoolchain_action("remove", "foo")
    assert "No such toolchain" in str(e.value)
