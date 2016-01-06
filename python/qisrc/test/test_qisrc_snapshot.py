## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisrc.snapshot

def test_simple(qisrc_action):
    qisrc_action.create_git_project("foo")
    qisrc_action.create_git_project("bar")
    res = qisrc_action("snapshot")
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.load(res)
    assert snapshot.format_version == 2


def test_with_argument(qisrc_action):
    qisrc_action.create_git_project("foo")
    qisrc_action.create_git_project("bar")
    res = qisrc_action("snapshot", "blah.xml")
    assert res == "blah.xml"
    snapshot = qisrc.snapshot.Snapshot()
    snapshot.load(res)
    assert snapshot.format_version == 2
