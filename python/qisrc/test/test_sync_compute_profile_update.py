## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.profile
from qisrc.sync import compute_profile_updates

def make_profiles(*args):
    res = dict()
    for (name, flags) in args:
        profile = qibuild.profile.Profile(name)
        profile.cmake_flags = flags
        res[profile.name] = profile
    return res

def test_remote_added():
    local = make_profiles()
    remote = make_profiles(
        ("foo", [("WITH_FOO", "ON")]),
    )
    new, updated = compute_profile_updates(local, remote)
    assert not updated
    assert len(new) == 1
    assert new[0] == remote["foo"]

def test_remote_updated():
    local = make_profiles(
        ("eggs", [("WITH_EGGS"), "ON"]),
        ("foo", [("WITH_FOO", "ON"), ("WITH_BAR", "OFF")]),
    )
    remote = make_profiles(
        ("eggs", [("WITH_EGGS"), "ON"]),
        ("foo", [("WITH_FOO", "ON")]),
    )
    new, updated = compute_profile_updates(local, remote)
    assert not new
    assert len(updated) == 1
    assert updated[0] == remote["foo"]

def test_same_remote():
    local = make_profiles(
        ("eggs", [("WITH_EGGS"), "ON"]),
        ("foo", [("WITH_FOO", "ON")]),
    )
    remote = make_profiles(
        ("eggs", [("WITH_EGGS"), "ON"]),
        ("foo", [("WITH_FOO", "ON")]),
    )
    new, updated = compute_profile_updates(local, remote)
    assert not new
    assert not updated

