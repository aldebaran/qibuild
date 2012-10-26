## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest

import qisys.worktree
import qibuild.toc


def open_toc_with_profiles(tmpdir, profiles=None, flags=None):
    dot_qi = tmpdir.mkdir(".qi")
    qibuild_xml = dot_qi.join("qibuild.xml")
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
    worktree = qisys.worktree.open_worktree(tmpdir.strpath)
    toc = qibuild.toc.Toc(worktree, cmake_flags=flags, profiles=profiles)
    return toc


def test_profiles_nothing_specified(tmpdir):
    toc = open_toc_with_profiles(tmpdir)
    assert toc.user_cmake_flags == list()
    assert "foo" not in toc.build_folder_name
    assert "bar" not in toc.build_folder_name

def test_one_profile(tmpdir):
    toc = open_toc_with_profiles(tmpdir, profiles=["foo"])
    assert toc.user_cmake_flags == ["WITH_FOO=ON"]
    assert "foo" in toc.build_folder_name
    assert "bar" not in toc.build_folder_name

def test_two_profiles(tmpdir):
    toc = open_toc_with_profiles(tmpdir, profiles=["foo", "bar"])
    assert toc.user_cmake_flags == ["WITH_FOO=ON", "WITH_BAR=ON"]
    assert "foo" in toc.build_folder_name
    assert "bar" in toc.build_folder_name

def test_profile_and_flags(tmpdir):
    toc = open_toc_with_profiles(tmpdir, profiles=["foo"], flags=["WITH_FOO=OFF"])
    # Note: we *could* detect that the user is overiding profiles flags from the
    # command line, and has conflicting options, but it's probably best to
    # let CMake use the last setting and be done with it.
    assert toc.user_cmake_flags == ["WITH_FOO=ON", "WITH_FOO=OFF"]

def test_non_existing_profile(tmpdir):
    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.toc.NoSuchProfile):
        toc = open_toc_with_profiles(tmpdir, profiles=["doesnotexist"])

def test_add_profile(tmpdir):
    worktree = qisys.worktree.create(tmpdir.strpath)
    qibuild_xml = tmpdir.join(".qi").join("qibuild.xml")
    profile = qibuild.profile.Profile("foo")
    profile.cmake_flags = ["FOO=BAR"]
    qibuild.profile.add_profile(qibuild_xml.strpath, profile)
    parsed = qibuild.profile.parse_profiles(qibuild_xml.strpath)
    assert len(parsed) == 1
    assert parsed["foo"] == profile
