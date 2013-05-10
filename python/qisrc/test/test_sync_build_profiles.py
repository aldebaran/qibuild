## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.profile
import qisrc.sync_build_profiles

from qibuild.test.conftest import TestBuildWorkTree

def test_remote_added(cd_to_tmpdir):
    build_worktree = TestBuildWorkTree()
    xml = """
<manifest>
  <profiles>
    <profile name="foo" />
  </profiles>
</manifest>
"""
    remote_xml = cd_to_tmpdir.join("remote.xml")
    remote_xml.write(xml)
    qibuild_xml = build_worktree.qibuild_xml
    qisrc.sync_build_profiles.sync_build_profiles(build_worktree,
                                                  remote_xml.strpath)
    profiles = qibuild.profile.parse_profiles(qibuild_xml)
    assert len(profiles) == 1
    assert "foo" in profiles

def test_remote_updated(cd_to_tmpdir, record_messages):
    build_worktree = TestBuildWorkTree()
    xml = """
<manifest>
  <profiles>
    <profile name="foo">
      <cmake>
        <flags>
          <flag name="FOO">BAR</flag>
        </flags>
      </cmake>
    </profile>
  </profiles>
</manifest>
"""
    remote_xml = cd_to_tmpdir.join("remote.xml")
    remote_xml.write(xml)
    qibuild_xml = build_worktree.qibuild_xml
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml,
                                            "foo",
                                            [('SPAM', 'EGGS')])
    qisrc.sync_build_profiles.sync_build_profiles(build_worktree,
                                                  remote_xml.strpath)
    assert record_messages.find("updated remotely")

    profiles = qibuild.profile.parse_profiles(qibuild_xml)
    assert len(profiles) == 1
    assert "foo" in profiles

def test_same_remote(cd_to_tmpdir, record_messages):
    build_worktree = TestBuildWorkTree()
    xml = """
<manifest>
  <profiles>
    <profile name="foo">
      <cmake>
        <flags>
          <flag name="FOO">BAR</flag>
        </flags>
      </cmake>
    </profile>
  </profiles>
</manifest>
"""
    remote_xml = cd_to_tmpdir.join("remote.xml")
    remote_xml.write(xml)
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml,
                                            "foo",
                                            [('FOO', 'BAR')])
    qisrc.sync_build_profiles.sync_build_profiles(build_worktree,
                                                  remote_xml.strpath)
    assert not record_messages.find("updated remotely")

