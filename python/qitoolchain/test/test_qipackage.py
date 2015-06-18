## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import qisys.archive
import qitoolchain.qipackage

def test_equality():
    foo = qitoolchain.qipackage.QiPackage("foo", "1.2")
    foo2 = qitoolchain.qipackage.QiPackage("foo", "1.2")
    foo3 = qitoolchain.qipackage.QiPackage("foo", "1.3")
    bar = qitoolchain.qipackage.QiPackage("bar", "1.2")

    assert foo == foo2
    assert foo2 < foo3
    assert foo != bar

def test_from_archive(tmpdir):
    foo = tmpdir.mkdir("foo")
    foo_xml = foo.join("package.xml")
    foo_xml.write("""<package name="foo" version="0.1"/>""")
    archive = qisys.archive.compress(foo.strpath, flat=True)
    package = qitoolchain.qipackage.from_archive(archive)
    assert package.name == "foo"
    assert package.version == "0.1"

def test_skip_package_xml(tmpdir):
    foo = tmpdir.mkdir("foo")
    foo_xml = foo.join("package.xml")
    foo_xml.write("""<package name="foo" version="0.1"/>""")
    foo.ensure("include", "foo.h", file=True)
    foo.ensure("lib", "libfoo.so", file=True)
    package = qitoolchain.qipackage.QiPackage("foo", path=foo.strpath)
    dest = tmpdir.join("dest")
    package.install(dest.strpath)
    assert dest.join("include", "foo.h").check(file=True)
    assert dest.join("lib", "libfoo.so").check(file=True)
    assert not dest.join("package.xml").check(file=True)

def test_reads_runtime_manifest(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost.h", file=True)
    boost_path.ensure("lib", "libboost.so", file=True)
    runtime_manifest = boost_path.ensure("install_manifest_runtime.txt", file=True)
    runtime_manifest.write("""\
lib/libboost.so
""")
    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    installed = package.install(dest.strpath, components=["runtime"])
    assert not dest.join("include", "boost.h").check(file=True)
    libbost_so = dest.join("lib", "libboost.so")
    assert libbost_so.check(file=True)
    assert installed == ["lib/libboost.so"]

def test_backward_compat_runtime_install(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost.h", file=True)
    boost_path.ensure("lib", "libboost.so", file=True)
    boost_path.ensure("package.xml", file=True)

    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    installed = package.install(dest.strpath, components=["runtime"])
    assert not dest.join("include", "boost.h").check(file=True)
    libbost_so = dest.join("lib", "libboost.so")
    assert libbost_so.check(file=True)
    assert installed == ["lib/libboost.so"]

def test_reads_release_mask(tmpdir):
    qt_path = tmpdir.mkdir("qt")
    qt_path.ensure("include", "qt.h", file=True)
    qt_path.ensure("lib", "QtCore4.lib", file=True)
    qt_path.ensure("lib", "QtCored4.lib", file=True)
    qt_path.ensure("bin", "QtCore4.dll", file=True)
    qt_path.ensure("bin", "QtCored4.dll", file=True)
    runtime_mask = qt_path.ensure("runtime.mask", file=True)
    runtime_mask.write("""\
# headers
exclude include/.*

# .lib
exclude lib/.*\.lib
""")
    release_mask = qt_path.ensure("release.mask", file=True)
    release_mask.write("""\
exclude bin/QtCored4.dll
""")
    package = qitoolchain.qipackage.QiPackage("qt", path=qt_path.strpath)
    dest = tmpdir.join("dest")
    package.install(dest.strpath, release=True, components=["runtime"])
    assert dest.join("bin", "QtCore4.dll").check(file=True)
    assert not dest.join("lib", "QtCored4.lib").check(file=True)

def test_include_in_mask(tmpdir):
    qt_path = tmpdir.mkdir("qt")
    qt_path.ensure("bin", "assitant.exe")
    qt_path.ensure("bin", "moc.exe")
    qt_path.ensure("bin", "lrelease.exe")
    qt_path.ensure("bin", "lupdate.exe")
    runtime_mask = qt_path.ensure("runtime.mask", file=True)
    runtime_mask.write("""\
exclude bin/.*\.exe
include bin/lrelease.exe
include bin/lupdate.exe
""")
    dest = tmpdir.join("dest")
    package = qitoolchain.qipackage.QiPackage("qt", path=qt_path.strpath)
    package.install(dest.strpath, release=True, components=["runtime"])
    assert dest.join("bin", "lrelease.exe").check(file=True)
    assert not dest.join("bin", "moc.exe").check(file=True)

def test_load_deps(tmpdir):
    libqi_path = tmpdir.mkdir("libqi")
    libqi_path.ensure("package.xml").write("""\
<package name="libqi">
  <depends testtime="true" names="gtest" />
  <depends runtime="true" names="boost python" />
</package>
""")
    package = qitoolchain.qipackage.QiPackage("libqi", path=libqi_path.strpath)
    package.load_deps()
    assert package.build_depends == set()
    assert package.run_depends == set(["boost", "python"])
    assert package.test_depends == set(["gtest"])

def test_extract_legacy_bad_top_dir(tmpdir):
    src = tmpdir.mkdir("src")
    boost = src.mkdir("boost")
    boost.ensure("lib", "libboost.so", file=True)
    res = qisys.archive.compress(boost.strpath)
    dest = tmpdir.mkdir("dest").join("boost-1.55")
    qitoolchain.qipackage.extract(res, dest.strpath)
    assert dest.join("lib", "libboost.so").check(file=True)

def test_extract_legacy_ok_top_dir(tmpdir):
    src = tmpdir.mkdir("src")
    boost = src.mkdir("boost-1.55")
    boost.ensure("lib", "libboost.so", file=True)
    res = qisys.archive.compress(boost.strpath)
    dest = tmpdir.mkdir("dest").join("boost-1.55")
    qitoolchain.qipackage.extract(res, dest.strpath)
    assert dest.join("lib", "libboost.so").check(file=True)

def test_extract_modern(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("package.xml", file=True)
    src.ensure("lib", "libboost.so", file=True)
    output = tmpdir.join("boost.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    dest = tmpdir.mkdir("dest").join("boost-1.55")
    qitoolchain.qipackage.extract(res, dest.strpath)
    assert dest.join("lib", "libboost.so").check(file=True)

def test_installing_test_component(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost.h", file=True)
    boost_path.ensure("lib", "libboost.so", file=True)
    boost_path.ensure("package.xml", file=True)

    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    installed = package.install(dest.strpath, components=["test", "runtime"])

    assert not dest.join("include", "boost.h").check(file=True)

def test_get_set_license(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.join("package.xml").write("""
<package name="boost" version="1.58" />
""")
    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    assert package.license is None
    package.license = "BSD"
    package2 = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    assert package2.license == "BSD"
