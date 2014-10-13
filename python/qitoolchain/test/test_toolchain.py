import os

import qitoolchain.toolchain

def get_tc_file_contents(tc):
    """ get the contents of the toolchain file of a toolchain

    """
    tc_file_path = tc.toolchain_file
    with open(tc_file_path, "r") as fp:
        contents = fp.read()
    return contents

def test_get_tc_names():
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain = qitoolchain.toolchain.Toolchain("baz")
    assert qitoolchain.get_tc_names() == ["bar", "baz"]

def test_persistent_storage(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    feed.add_package(boost_package, with_url=True)
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    toolchain2 = qitoolchain.get_toolchain("bar")
    assert toolchain2.packages == toolchain.packages

def test_stores_feed_after_updating(feed):
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    toolchain2 = qitoolchain.toolchain.Toolchain("bar")
    assert toolchain2.feed_url == feed.url

def test_toolchain_file(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    feed.add_package(boost_package, with_url=True)
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    boost_path = toolchain.db.get_package_path("boost")
    tc_contents = get_tc_file_contents(toolchain)
    assert ('list(INSERT CMAKE_PREFIX_PATH 0 "%s")' % boost_path) in tc_contents

def test_add_local_ctc(tmpdir):
    ctc = tmpdir.mkdir("ctc")
    toolchain_xml = ctc.join("toolchain.xml")
    toolchain_xml.write("""
<toolchain>
  <package name="ctc"
           cross_gdb="cross/bin/i686-linux-gnu-gdb"
           sysroot="sysroot"
           toolchain_file="cross-config.cmake"
           directory="."
  />
  <package name="boost" directory="boost" />
</toolchain>
""")
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(toolchain_xml.strpath)
    tc_contents = get_tc_file_contents(toolchain)
    ctc_path = toolchain.db.get_package_path("ctc")
    config_cmake = os.path.join(ctc_path, "cross-config.cmake")
    assert ('include("%s")' % config_cmake) in tc_contents


def test_removing(feed):
    boost_package = qitoolchain.qipackage.QiPackage("boost", "1.42")
    feed.add_package(boost_package, with_url=True)
    toolchain = qitoolchain.toolchain.Toolchain("bar")
    toolchain.update(feed.url)
    toolchain.remove()
    toolchain2 = qitoolchain.toolchain.Toolchain("bar")
    assert not toolchain2.packages
