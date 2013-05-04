## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from StringIO import StringIO

import qisys
import qisys.worktree
import qibuild.profile
import qisrc.sync_build_profiles

from qisrc.test.conftest import TestGitWorkTree
from qibuild.test.conftest import TestBuildWorkTree

def test_remote_added(cd_to_tmpdir):
    git_worktee = TestGitWorkTree()
    build_worktree = TestBuildWorkTree()
    xml = """
<manifest>
  <profiles>
    <profile name="foo" />
  </profiles>
</manifest>
"""
    qibuild_xml = build_worktree.qibuild_xml
    qisrc.sync_build_profiles.sync_build_profiles(build_worktree, StringIO(xml))
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
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml,
                                            "foo",
                                            [('SPAM', 'EGGS')])
    qisrc.sync_build_profiles.sync_build_profiles(build_worktree, StringIO(xml))
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
    qibuild_xml = build_worktree.qibuild_xml
    qibuild.profile.configure_build_profile(qibuild_xml,
                                            "foo",
                                            [('FOO', 'BAR')])
    qisrc.sync_build_profiles.sync_build_profiles(build_worktree, StringIO(xml))
    assert not record_messages.find("updated remotely")

