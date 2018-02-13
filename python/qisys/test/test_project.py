# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

from qisys.test.conftest import TestWorkTree

# allow the existing foo/bar/baz names
# pylint: disable=blacklisted-name


def test_get_set_license(worktree):
    foo = worktree.create_project("foo")
    assert foo.license is None
    foo.license = "GPL"
    assert foo.license == "GPL"
    worktree2 = TestWorkTree()
    foo2 = worktree2.get_project("foo")
    assert foo2.license == "GPL"
