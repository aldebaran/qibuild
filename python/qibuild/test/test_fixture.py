## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def test_add_test_project(build_worktree):
    world = build_worktree.add_test_project("world")
    assert build_worktree.get_build_project("world")
