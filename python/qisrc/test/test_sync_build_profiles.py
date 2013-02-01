## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from StringIO import StringIO

import mock

import qisys
import qisys.worktree
import qibuild.profile
import qisrc.sync_build_profiles

def test_remote_added(tmpdir):
    worktree = qisys.worktree.create(tmpdir.strpath)
    xml = """
<manifest>
  <profiles>
    <profile name="foo" />
  </profiles>
</manifest>
"""
    qisrc.sync_build_profiles.sync_build_profiles(worktree, StringIO(xml))
    profiles = qibuild.profile.parse_profiles(worktree.qibuild_xml)
    assert len(profiles) == 1
    assert "foo" in profiles

def test_remote_updated(tmpdir):
    worktree = qisys.worktree.create(tmpdir.strpath)
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
    qibuild_xml = tmpdir.join(".qi", "qibuild.xml")
    qibuild_xml.write("""
<manifest>
  <profiles>
    <profile name="foo">
      <cmake>
        <flags>
          <flag name="SPAM">EGGS</flag>
        </flags>
      </cmake>
    </profile>
  </profiles>
</manifest>
""")
    # Just a warning for now ...
    with mock.patch("qisys.ui.warning") as warning_mock:
        qisrc.sync_build_profiles.sync_build_profiles(worktree, StringIO(xml))

    assert warning_mock.called

    profiles = qibuild.profile.parse_profiles(worktree.qibuild_xml)
    assert len(profiles) == 1
    assert "foo" in profiles

def test_same_remote(tmpdir):
    worktree = qisys.worktree.create(tmpdir.strpath)
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
    qibuild_xml = tmpdir.join(".qi", "qibuild.xml")
    qibuild_xml.write("""
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
""")
    # Just a warning for now ...
    with mock.patch("qisys.ui.warning") as warning_mock:
        qisrc.sync_build_profiles.sync_build_profiles(worktree, StringIO(xml))

    assert not warning_mock.called
