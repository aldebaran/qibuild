## Copyright (c) 2012-2014 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


import qibuild.profile

def test_read_build_profiles(tmpdir):
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
    assert qibuild.profile.get_cmake_flags(qibuild_xml.strpath,
                                            ["bar", "foo"]) == \
            [("WITH_BAR", "ON"), ("WITH_FOO", "ON")]

def test_profiles_are_persistent(tmpdir):
    qibuild_xml = tmpdir.join("qibuild.xml")
    qibuild_xml.write("<qibuild />")
    qibuild.profile.configure_build_profile(qibuild_xml.strpath, "foo", [("WITH_FOO", "ON")])
    assert qibuild.profile.parse_profiles(qibuild_xml.strpath)["foo"].cmake_flags == \
            [("WITH_FOO", "ON")]
    qibuild.profile.remove_build_profile(qibuild_xml.strpath, "foo")
    assert "foo" not in qibuild.profile.parse_profiles(qibuild_xml.strpath)

