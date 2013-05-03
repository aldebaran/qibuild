## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file

import os
import pytest
import subprocess

import qisys.script
from qibuild.test.test_toc import TestToc

def test_update(toc, trad):
    fr_FR_po_file = os.path.join(trad.path, "po", "fr_FR.po")
    en_US_po_file = os.path.join(trad.path, "po", "en_US.po")
    pot_file = os.path.join(trad.path, "po", "translate.pot")
    assert not os.path.exists(fr_FR_po_file)
    assert not os.path.exists(en_US_po_file)
    assert not os.path.exists(pot_file)
    qisys.script.run_action("qilinguist.actions.update",
                           args=["translate", "--worktree", toc.worktree.root])
    assert os.path.exists(fr_FR_po_file)
    assert os.path.exists(en_US_po_file)
    assert os.path.exists(pot_file)

def test_release(toc, trad):
    fr_FR_mo_file = os.path.join(trad.path, "po", "share", "locale", "translate", "fr_FR", "LC_MESSAGES", "translate.mo")
    en_US_mo_file = os.path.join(trad.path, "po", "share", "locale", "translate", "fr_FR", "LC_MESSAGES", "translate.mo")
    assert not os.path.exists(fr_FR_mo_file)
    assert not os.path.exists(en_US_mo_file)
    qisys.script.run_action("qilinguist.actions.update",
                            args=["translate", "--worktree", toc.worktree.root])
    qisys.script.run_action("qilinguist.actions.release",
                            args=["translate", "--worktree", toc.worktree.root])
    assert os.path.exists(fr_FR_mo_file)
    assert os.path.exists(en_US_mo_file)


def create_trad():
    with TestToc() as toc:
        proj = toc.get_project("translate")
        fr_FR_po_file = os.path.join(proj.path, "po", "fr_FR.po")
        en_US_po_file = os.path.join(proj.path, "po", "en_US.po")
        fr_file = open(fr_FR_po_file, 'wb')
        en_file = open(en_US_po_file, 'wb')
        fr_file.write("""
# French translations for qi package
# Traductions fran\xc3\xa7aises du paquet qi.
# Copyright (C) 2012 THE qi'S COPYRIGHT HOLDER
# This file is distributed under the same license as the qi package.
# Automatically generated, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: qi 1.16\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-10-09 15:15+0200\\n"
"PO-Revision-Date: 2012-10-09 15:15+0200\\n"
"Last-Translator: Automatically generated\\n"
"Language-Team: none\\n"
"Language: fr\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n > 1);\\n"
"X-Language: fr_FR\\n"

#: main.cpp:15
msgid "Brian is in the kitchen."
msgstr "Brian est dans la cuisine."

#: main.cpp:13
msgid "Hi, my name is NAO."
msgstr "Bonjour, mon nom est NAO."

#: main.cpp:14
msgid "Where is Brian?"
msgstr "O\xc3\xb9 est Brian ?"
""")
        en_file.write("""
# English translations for qi package.
# Copyright (C) 2012 THE qi'S COPYRIGHT HOLDER
# This file is distributed under the same license as the qi package.
# Automatically generated, 2012.
#
msgid ""
msgstr ""
"Project-Id-Version: qi 1.16\\n"
"Report-Msgid-Bugs-To: \\n"
"POT-Creation-Date: 2012-10-09 15:15+0200\\n"
"PO-Revision-Date: 2012-10-09 15:15+0200\\n"
"Last-Translator: Automatically generated\\n"
"Language-Team: none\\n"
"Language: en_US\\n"
"MIME-Version: 1.0\\n"
"Content-Type: text/plain; charset=UTF-8\\n"
"Content-Transfer-Encoding: 8bit\\n"
"Plural-Forms: nplurals=2; plural=(n != 1);\\n"
"X-Language: en_US\\n"

#: main.cpp:15
msgid "Brian is in the kitchen."
msgstr "Brian is in the kitchen."

#: main.cpp:13
msgid "Hi, my name is NAO."
msgstr "Hi, my name is NAO."

#: main.cpp:14
msgid "Where is Brian?"
msgstr "Where is Brian?"

""")
        fr_file.close()
        en_file.close()

@pytest.mark.slow
def test_cplusplus_sdk_workflow(toc, trad):
    create_trad()
    qisys.script.run_action("qilinguist.actions.update",
                           args=["translate", "--worktree", toc.worktree.root])
    qisys.script.run_action("qilinguist.actions.release",
                           args=["translate", "--worktree", toc.worktree.root])
    toc.configure_project(trad)
    toc.build_project(trad)

    ## check binary output
    binary = os.path.join(trad.sdk_directory, "bin", "translate")
    dictPath = os.path.join(trad.path, "po", "share", "locale", "translate")
    env = os.environ.copy()
    env["LANGUAGE"] = "fr_FR.UTF-8"
    cmd = [binary, dictPath]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_fr = """Bonjour, mon nom est NAO.
O\xc3\xb9 est Brian ?
Brian est dans la cuisine.
"""
    assert out_fr in out

    env = os.environ.copy()
    env["LANGUAGE"] = "en_US.UTF-8"
    cmd = [binary, dictPath]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr = subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_en = """Hi, my name is NAO.
Where is Brian?
Brian is in the kitchen.
"""
    assert out_en in out


def test_cplusplus_install_workflow(toc, trad, tmpdir):
    create_trad()
    create_trad()
    qisys.script.run_action("qilinguist.actions.update",
                           args=["translate", "--worktree", toc.worktree.root])
    qisys.script.run_action("qilinguist.actions.release",
                           args=["translate", "--worktree", toc.worktree.root])

    toc.configure_project(trad)
    toc.build_project(trad)
    toc.install_project(trad, tmpdir.strpath)

    ## check mo files
    fr_FR_mo_file = tmpdir.join("share", "locale", "translate", "fr_FR", "LC_MESSAGES", "translate.mo").strpath
    en_US_mo_file = tmpdir.join("share", "locale", "translate", "en_US", "LC_MESSAGES", "translate.mo").strpath
    assert os.path.exists(fr_FR_mo_file)
    assert os.path.exists(en_US_mo_file)

    ## check binary output
    binary = tmpdir.join("bin", "translate").strpath
    dictPath = tmpdir.join("share", "locale", "translate").strpath
    env = os.environ.copy()
    env["LANGUAGE"] = "fr_FR.UTF-8"
    cmd = [binary, dictPath]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_fr = """Bonjour, mon nom est NAO.
O\xc3\xb9 est Brian ?
Brian est dans la cuisine.
"""
    assert out_fr in out

    env = os.environ.copy()
    env["LANGUAGE"] = "en_US.UTF-8"
    cmd = [binary, dictPath]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_en = """Hi, my name is NAO.
Where is Brian?
Brian is in the kitchen.
"""
    assert out_en in out
