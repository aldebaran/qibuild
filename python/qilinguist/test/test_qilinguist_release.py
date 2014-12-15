import qisys.script

import pytest

def test_pml_outside_worktree(tmpdir, monkeypatch):
    foo = tmpdir.mkdir("foo")
    pml_path = foo.join("foo.pml")
    pml_path.write("""
<Package name="foo" format_version="4">
  <Translations>
    <Translation name="foo_fr_FR"
                 src="translations/foo_fr_FR.ts"
                 language="fr_FR" />
  </Translations>

</Package>
""")
    translations_dir = foo.mkdir("translations")
    translations_dir.join("foo_fr_FR.ts").write("""
<TS language="fr_FR" version="2.1">
  <context>
    <name>QApplication</name>
    <message>
      <location filename="../main.cpp" line="24" />
      <source>Hello world!</source>
      <translation>Bonjour, monde</translation>
    </message>
  </context>
</TS>
""")
    monkeypatch.chdir(foo)
    qisys.script.run_action("qilinguist.actions.release", [pml_path.strpath])
    qm_path = translations_dir.join("foo_fr_FR.qm")
    assert qm_path.check(file=True)


def test_raise_when_no_project_given_outside_a_worktree(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    with pytest.raises(Exception) as e:
        qisys.script.run_action("qilinguist.actions.release")
    assert "outside a worktree" in e.value.message
