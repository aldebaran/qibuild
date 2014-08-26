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
