#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import pytest

import qisys.script
from qibuild.test.conftest import TestBuildWorkTree


def test_pml_outside_worktree(tmpdir, monkeypatch):
    """ Test Pml Outside Worktree """
    foo1 = tmpdir.mkdir("foo")
    pml_path = foo1.join("foo.pml")
    pml_path.write("""
<Package name="foo" format_version="4">
  <Translations>
    <Translation name="foo_fr_FR"
                 src="translations/foo_fr_FR.ts"
                 language="fr_FR" />
  </Translations>

</Package>
""")
    translations_dir = foo1.mkdir("translations")
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
    monkeypatch.chdir(foo1)
    qisys.script.run_action("qilinguist.actions.release", [pml_path.strpath])
    qm_path = translations_dir.join("foo_fr_FR.qm")
    assert qm_path.check(file=True)


def test_raise_when_no_project_given_outside_a_worktree(tmpdir, monkeypatch):
    """ Test Raise When No Project Given Outside A Worktree """
    monkeypatch.chdir(tmpdir)
    with pytest.raises(Exception) as e:
        qisys.script.run_action("qilinguist.actions.release")
    assert "outside a worktree" in str(e)


def test_non_translated_messages_gettext(qilinguist_action, record_messages):
    """ Test Non Translated Messages GetText """
    trad_project = qilinguist_action.trad
    qilinguist_action.create_po(trad_project)
    main_cpp = os.path.join(trad_project.path, "main.cpp")
    with open(main_cpp, "a") as fp:
        fp.write("""\nchar* foo() {\n    return _("Hello, world");\n}\n""")
    qilinguist_action("update", "translate")
    qilinguist_action("release", "translate", raises=True)
    assert record_messages.find("untranslated")


def test_non_translated_messages_qt(qilinguist_action):
    """ Test Non Translated Massages Qt """
    build_worktree = TestBuildWorkTree()
    _project = build_worktree.add_test_project("translateme/qt")
    qilinguist_action("update", "helloqt")
    qilinguist_action("release", "helloqt", raises=True)


def test_invalid_po_file(qilinguist_action):
    """ Test Invalid Po File """
    trad_project = qilinguist_action.trad
    qilinguist_action.create_po(trad_project)
    fr_FR_po = os.path.join(trad_project.path, "po", "fr_FR.po")
    with open(fr_FR_po, "a") as fp:
        fp.write("""\n#: broken\nsyntax-error\n""")
    error = qilinguist_action("release", "translate", raises=True)
    assert "failed" in str(error)
