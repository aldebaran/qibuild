## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qibuild.test.conftest import TestBuildWorkTree

def test_simple(qilinguist_action, record_messages):
    build_worktree = TestBuildWorkTree()
    build_worktree.add_test_project("translateme/qt")
    qilinguist_action("list")
    assert record_messages.find("\*\s+helloqt")
    assert record_messages.find("\*\s+translate")
