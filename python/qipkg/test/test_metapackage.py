import qipkg.metapackage

def test_meta(worktree):
    tmpdir = worktree.tmpdir
    meta_pml = tmpdir.ensure("meta.mpml", file=True)
    meta_pml.write("""
<metapackage name="meta" version="0.1">
  <include src="a/a.pml" />
  <include src="b/b.mpml" />

</metapackage>
""")
    a_pml = tmpdir.ensure("a/a.pml", file=True)
    a_pml.write("""
<package />
""")
    b_mpml = tmpdir.ensure("b/b.mpml", file=True)
    b_mpml.write("""
<metapackage name="b">
  <include src="c/c.pml" />
</metapackage>
""")
    c_pml = tmpdir.ensure("c/c.pml", file=True)
    c_pml.write("""
<package />
""")
    meta_pml = qipkg.metapackage.MetaPackage(meta_pml.strpath)
    assert meta_pml.pml_paths == ["a/a.pml", "c/c.pml"]
