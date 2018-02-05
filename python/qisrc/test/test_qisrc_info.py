# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.


def test_qisrc_info(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    qisrc_action("init", manifest_url)
    qisrc_action("info")
    found_url = record_messages.find("url")
    assert "manifest.git" in found_url
    assert not record_messages.find("groups:")


def test_qisrc_info_with_groups(qisrc_action, git_server, record_messages):
    manifest_url = git_server.manifest_url
    git_server.create_group("mygroup", ["a", "b"])
    qisrc_action("init", manifest_url, "-g", "mygroup")
    qisrc_action("info")
    found_url = record_messages.find("url")
    assert "manifest.git" in found_url
    assert record_messages.find("groups:")
    assert record_messages.find("mygroup")
