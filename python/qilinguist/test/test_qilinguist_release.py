## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

import qisys.command
import qisys.error
import qisys.script

from qibuild.test.conftest import TestBuildWorkTree
from qilinguist.test.conftest import skip_no_gettext
from qilinguist.test.conftest import skip_no_lrelease

import pytest

@skip_no_lrelease
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
    # pylint:disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qisys.script.run_action("qilinguist.actions.release")
    assert "outside a worktree" in e.value.message

@skip_no_gettext
def test_non_translated_messages_gettext(qilinguist_action, record_messages):
    trad_project = qilinguist_action.trad
    qilinguist_action.create_po(trad_project)
    main_cpp = os.path.join(trad_project.path, "main.cpp")
    with open(main_cpp, "a") as fp:
        fp.write("""
char* foo() {
    return _("Hello, world");
}
""")
    qilinguist_action("update", "translate")
    qilinguist_action("release", "translate", raises=True)
    assert record_messages.find("untranslated")

@skip_no_lrelease
def test_non_translated_messages_qt(qilinguist_action):
    build_worktree = TestBuildWorkTree()
    project = build_worktree.add_test_project("translateme/qt")
    qilinguist_action("update", "helloqt")
    qilinguist_action("release", "helloqt", raises=True)

@skip_no_gettext
def test_invalid_po_file(qilinguist_action):
    trad_project = qilinguist_action.trad
    qilinguist_action.create_po(trad_project)
    fr_FR_po = os.path.join(trad_project.path, "po", "fr_FR.po")
    with open(fr_FR_po, "a") as fp:
        fp.write("""
#: broken
syntax-error
""")
    error = qilinguist_action("release", "translate", raises=True)
    assert "failed" in error
