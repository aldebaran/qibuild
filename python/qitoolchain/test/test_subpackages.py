import qisys
import qitoolchain.toolchain


def test_subpackage_parsing(tmpdir):
    tmp = tmpdir.mkdir("feed")
    subpackage_xml = tmp.join("subpackage.xml")
    subpackage_xml.write("""
<toolchain>
  <package name="rootpkg" directory="." version="1.0">
    <package name="subpkg1" version="2.3"/>
    <package name="subpkg2" version="0.2"/>
  </package>
</toolchain>""")
    parser = qitoolchain.feed.ToolchainFeedParser("test_subpackage")
    parser.parse(subpackage_xml.strpath)
    pkgs = parser.get_packages()

    toolchain_path = qisys.sh.get_share_path("qi", "toolchains", parser.name, "rootpkg")
    assert len(pkgs) == 3
    assert pkgs[0].name == "rootpkg"
    assert pkgs[1].name == "subpkg1"
    assert pkgs[2].name == "subpkg2"
    assert pkgs[1].directory == toolchain_path
    assert pkgs[2].directory == toolchain_path
