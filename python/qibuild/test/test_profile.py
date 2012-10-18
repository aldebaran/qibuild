## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest

import qisrc.worktree
import qibuild.toc


def write_foo_profile(tmpdir):
    qibuild_xml = tmpdir.join(".qi").join("qibuild.xml")
    qibuild_xml.write("""
<qibuild version="1">
 <profiles>
   <profile name="foo">
    <cmake>
      <flags>
        <flag name="ENABLE_FOO">ON</flag>
      </flags>
    </cmake>
   </profile>
  </profiles>
</qibuild>
""")


def test_default_toc(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    toc = qibuild.toc.Toc(worktree)
    assert toc.user_cmake_flags == list()

def test_passing_flags_on_command_line(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    toc = qibuild.toc.Toc(worktree, cmake_flags=["FOO=BAR"])
    assert toc.user_cmake_flags == ["FOO=BAR"]

def test_using_profile(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    write_foo_profile(tmpdir)
    toc = qibuild.toc.Toc(worktree, profile="foo")
    assert toc.user_cmake_flags == ["ENABLE_FOO=ON"]

def test_no_such_profile(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    write_foo_profile(tmpdir)
    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.toc.NoSuchProfile):
        qibuild.toc.Toc(worktree, profile="bar")

def test_using_profile_with_cmake_flags(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    write_foo_profile(tmpdir)
    toc = qibuild.toc.Toc(worktree, profile="foo",
                          cmake_flags=["ENABLE_BAR=ON"])
    assert toc.user_cmake_flags == ["ENABLE_FOO=ON", "ENABLE_BAR=ON"]

def test_using_default_profile(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    qibuild_xml = tmpdir.join(".qi").join("qibuild.xml")
    qibuild_xml.write("""
<qibuild version="1">
 <defaults profile="foo" />
 <profiles>
   <profile name="foo">
    <cmake>
      <flags>
       <flag name="ENABLE_FOO">ON</flag>
      </flags>
    </cmake>
   </profile>
  </profiles>
</qibuild>
""")
    toc = qibuild.toc.Toc(worktree)
    assert toc.user_cmake_flags == ["ENABLE_FOO=ON"]


def test_wrong_default_profile(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    qibuild_xml = tmpdir.join(".qi").join("qibuild.xml")
    qibuild_xml.write("""
<qibuild version="1">
 <defaults profile="bar" />
 <profiles>
   <profile name="foo" />
  </profiles>
</qibuild>
""")
    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.toc.WrongDefaultProfile):
        qibuild.toc.Toc(worktree)

def test_add_profile(tmpdir):
    worktree = qisrc.worktree.create(tmpdir.strpath)
    qibuild_xml = tmpdir.join(".qi").join("qibuild.xml")
    profile = qibuild.profile.Profile("foo")
    profile.cmake_flags = ["FOO=BAR"]
    qibuild.profile.add_profile(qibuild_xml.strpath, profile)
    parsed = qibuild.profile.parse_profiles(qibuild_xml.strpath)
    assert len(parsed) == 1
    assert parsed["foo"] == profile
