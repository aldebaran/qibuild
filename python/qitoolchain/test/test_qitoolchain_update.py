## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

def test_update_local_ctc(qitoolchain_action, tmpdir):
    ctc_path = tmpdir.join("ctc").ensure(dir=True)
    ctc_path.join("toolchain.xml").write("""
<toolchain>
 <package name="ctc"
          directory="."
 />
</toolchain>
""")
    toolchain_xml = ctc_path.join("toolchain.xml")
    qitoolchain_action("create", "ctc", toolchain_xml.strpath)
    qitoolchain_action("update", "ctc", toolchain_xml.strpath)
    assert ctc_path.check(dir=True)

def test_update_no_feed(qitoolchain_action):
    qitoolchain_action("create", "foo")
    error = qitoolchain_action("update", "foo", raises=True)
    assert "Could not find feed" in error

def test_udpate_all_toolchains(qitoolchain_action, feed, record_messages):
    qitoolchain_action("create", "foo", feed.url)
    qitoolchain_action("create", "bar")
    qitoolchain_action("update")
    assert record_messages.find("These toolchains will be skipped because they have no feed: bar")
    assert record_messages.find("Updating foo")
