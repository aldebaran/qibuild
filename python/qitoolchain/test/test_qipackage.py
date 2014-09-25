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

def test_reads_runtime_mask(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost.h", file=True)
    boost_path.ensure("lib", "libboost.so", file=True)
    runtime_mask = boost_path.ensure("runtime.mask", file=True)
    runtime_mask.write("""\
/include/boost.h
""")
    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    package.install(dest.strpath, runtime=True)
    assert not dest.join("include", "boost.h").check(file=True)
    assert dest.join("lib", "libboost.so").check(file=True)

def test_reads_release_mask(tmpdir):
    qt_path = tmpdir.mkdir("qt")
    qt_path.ensure("include", "qt.h", file=True)
    qt_path.ensure("lib", "QtCore4.lib", file=True)
    qt_path.ensure("lib", "QtCored4.lib", file=True)
    qt_path.ensure("bin", "QtCore4.dll", file=True)
    qt_path.ensure("bin", "QtCored4.dll", file=True)
    release_mask = qt_path.ensure("release.mask", file=True)
    release_mask.write("""\
/lib/QtCored4.lib
/bin/QtCored4.dll
""")
    package = qitoolchain.qipackage.QiPackage("qt", path=qt_path.strpath)
    dest = tmpdir.join("dest")
    package.install(dest.strpath, release=True, runtime=True)
    assert dest.join("lib", "QtCore4.lib").check(file=True)
    assert not dest.join("lib", "QtCored4.lib").check(file=True)

def test_regexp_mask(tmpdir):
    boost_path = tmpdir.mkdir("boost")
    boost_path.ensure("include", "boost", "version.hpp", file=True)
    boost_path.ensure("lib", "libboost_filesystem.so", file=True)
    runtime_mask = boost_path.join("runtime.mask")
    runtime_mask.write("""\
/include/.*
""")
    package = qitoolchain.qipackage.QiPackage("boost", path=boost_path.strpath)
    dest = tmpdir.join("dest")
    package.install(dest.strpath, runtime=True)
    assert not dest.join("include", "boost", "version.hpp").check(file=True)
    assert dest.join("lib", "libboost_filesystem.so").check(file=True)
