#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" ConfTest """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import py

import qilinguist.worktree
from qisys.test.conftest import *  # pylint:disable=W0401,W0614
from qibuild.test.conftest import *  # pylint:disable=W0401,W0614


class QiLinguistAction(TestAction):
    """ QiLinguistAction Class """

    def __init__(self, worktree_root=None):
        """ QiLinguistAction Init """
        super(QiLinguistAction, self).__init__("qilinguist.actions")
        self.build_worktree = TestBuildWorkTree()
        self.trad = self.build_worktree.add_test_project("translateme/gettext")

    def create_po(self, proj):
        """ Create Po """
        fr_FR_po_file = os.path.join(proj.path, "po", "fr_FR.po")
        en_US_po_file = os.path.join(proj.path, "po", "en_US.po")
        fr_file = open(fr_FR_po_file, 'wb')
        en_file = open(en_US_po_file, 'wb')
        fr_file.write(b"""
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
        en_file.write(b"""
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


class TestLinguistWorktree(qilinguist.worktree.LinguistWorkTree):
    """ TestLinguistWorktree Class """

    def __init__(self, worktree=None):
        """ TestLinguistWorktree Init """
        if not worktree:
            worktree = TestWorkTree()
        super(TestLinguistWorktree, self).__init__(worktree)
        self.tmpdir = py.path.local(self.root)  # pylint:disable=no-member

    def create_gettext_project(self, name):
        """ Create GetText Project """
        proj_path = os.path.join(self.root, name)
        qisys.sh.mkdir(proj_path, recursive=True)
        qiproject_xml = os.path.join(proj_path, "qiproject.xml")
        with open(qiproject_xml, "w") as fp:
            fp.write("""
<project version="3">
    <qilinguist name="{name}" tr="gettext" linguas="fr_FR en_US" />
</project>
""".format(name=name))
        self.worktree.add_project(name)
        return self.get_linguist_project(name, raises=True)


@pytest.fixture
def qilinguist_action(cd_to_tmpdir):
    """ QiLinguits Action """
    return QiLinguistAction()


@pytest.fixture
def linguist_worktree(cd_to_tmpdir):
    """ Linguits Worktree """
    return TestLinguistWorktree()
