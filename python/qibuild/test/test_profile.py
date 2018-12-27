#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Test Profile """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qibuild.config
import qibuild.profile
from qibuild.test.conftest import TestBuildWorkTree
from qisrc.test.conftest import qisrc_action, git_server


def test_read_build_profiles(tmpdir):
    """ Test Read Build Profile """
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("""
<qibuild version="1">
  <profiles>
    <profile name="foo">
      <cmake>
        <flags>
          <flag name="WITH_FOO">ON</flag>
        </flags>
      </cmake>
    </profile>
    <profile name="bar">
      <cmake>
        <flags>
          <flag name="WITH_BAR">ON</flag>
        </flags>
      </cmake>
    </profile>
  </profiles>
</qibuild>
""")
    profiles = qibuild.profile.parse_profiles(qibuild_xml.strpath)
    assert len(profiles) == 2
    assert profiles['foo'].cmake_flags == [("WITH_FOO", "ON")]
    assert profiles['bar'].cmake_flags == [("WITH_BAR", "ON")]


def test_profiles_are_persistent(tmpdir):
    """ Test Profiles Are Persistent """
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("<qibuild />")
    qibuild.profile.configure_build_profile(qibuild_xml.strpath, "foo", [("WITH_FOO", "ON")])
    assert qibuild.profile.parse_profiles(qibuild_xml.strpath)["foo"].cmake_flags == \
        [("WITH_FOO", "ON")]
    qibuild.profile.remove_build_profile(qibuild_xml.strpath, "foo")
    assert "foo" not in qibuild.profile.parse_profiles(qibuild_xml.strpath)


def test_using_custom_profile(qibuild_action, qisrc_action, git_server, record_messages):
    """ Test Using Custom Profile """
    git_server.add_build_profile("foo", [("WITH_FOO", "ON")])
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml, "bar", [("WITH_BAR", "ON")])
    build_worktree.create_project("spam")
    qibuild.config.add_build_config("foo", profiles=["foo"])
    qibuild.config.add_build_config("bar", profiles=["bar"])
    qibuild_action("configure", "spam", "--config", "foo", "--summarize-options")
    assert record_messages.find(r"WITH_FOO\s+: ON")
    record_messages.reset()
    qibuild_action("configure", "spam", "--config", "bar", "--summarize-options")
    assert record_messages.find(r"WITH_BAR\s+: ON")


def test_warns_on_conflict(qibuild_action, qisrc_action, git_server, record_messages):
    """ Test Warns On Conflict """
    git_server.add_build_profile("foo", [("WITH_FOO", "ON")])
    qisrc_action("init", git_server.manifest_url)
    build_worktree = TestBuildWorkTree()
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml, "foo", [("WITH_FOO", "OFF")])
    build_worktree.create_project("spam")
    qibuild.config.add_build_config("foo", profiles=["foo"])
    record_messages.reset()
    qibuild_action("configure", "spam", "--config", "foo", "--summarize-options")
    assert record_messages.find(r"WITH_FOO\s+: OFF")
    assert record_messages.find("WARN")
