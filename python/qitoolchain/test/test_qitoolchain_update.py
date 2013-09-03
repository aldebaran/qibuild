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
