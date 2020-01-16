#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import mock
import six


def test_simple_build(qidoc_action):
    """ Test Simple Build """
    qidoc_action.add_test_project("libqi")
    qidoc_action("build", "qi-api")


def test_translated_project(qidoc_action):
    """ Test Translated Project """
    translateme_proj = qidoc_action.add_test_project("translateme")
    # should build the english version without warnings
    qidoc_action("build", "translateme", "--werror")
    expected_index_html = os.path.join(translateme_proj.path,
                                       "build-doc", "html", "en", "index.html")
    assert os.path.exists(expected_index_html)
    if six.PY3:
        with open(expected_index_html, "r", encoding='utf-8') as fp:
            assert "This Page" in fp.read()
    else:
        with open(expected_index_html, "r") as fp:
            assert "This Page" in fp.read().decode("utf-8")

    # should build the french version
    qidoc_action("build", "translateme", "--language", "fr")
    expected_index_html = os.path.join(translateme_proj.path,
                                       "build-doc", "html", "fr", "index.html")
    assert os.path.exists(expected_index_html)
    if six.PY3:
        with open(expected_index_html, "r", encoding='utf-8') as fp:
            assert "Cette page" in fp.read()
    else:
        with open(expected_index_html, "r") as fp:
            assert "Cette page" in fp.read().decode("utf-8")


def write_french_po(proj_path):
    """ Write French Po """
    po_file = os.path.join(proj_path, "source", "locale",
                           "fr", "LC_MESSAGES", "index.po")
    with open(po_file, "w") as fp:
        fp.write(""" #
msgid ""
msgstr ""
"Project-Id-Version: translateme latest\n"
"Report-Msgid-Bugs-To: \n"
"POT-Creation-Date: 2015-07-07 16:59\n"
"PO-Revision-Date: YEAR-MO-DA HO:MI+ZONE\n"
"Last-Translator: FULL NAME <EMAIL@ADDRESS>\n"
"Language-Team: LANGUAGE <LL@li.org>\n"
"MIME-Version: 1.0\n"
"Content-Type: text/plain; charset=UTF-8\n"
"Content-Transfer-Encoding: 8bit\n"

#: ../../source/index.rst:2
msgid "Welcome to the world's best doc !"
msgstr "Bienvenue sur la meilleure doc du monde !"

#: ../../source/index.rst:5
msgid "Introduction"
msgstr ""

#: ../../source/index.rst:7
msgid "This is a sentence to be translated"
msgstr ""

""")


def test_full_translation_workflow(qidoc_action):
    """ Test Full Translation Workflow """
    translateme_proj = qidoc_action.add_test_project("translateme")
    qidoc_action("intl-update", "translateme")
    write_french_po(translateme_proj.path)
    qidoc_action("build", "translateme", "--language", "fr")
    expected_index_html = os.path.join(translateme_proj.path,
                                       "build-doc", "html", "fr", "index.html")
    assert os.path.exists(expected_index_html)
    if six.PY3:
        with open(expected_index_html, "r", encoding='utf-8') as fp:
            assert "Bienvenue" in fp.read()
    else:
        with open(expected_index_html, "r") as fp:
            assert "Bienvenue" in fp.read().decode("utf-8")


def test_language_not_in_qiproject(qidoc_action):
    """ Test Language Not In QiProject """
    qidoc_action.add_test_project("translateme")
    error = qidoc_action("build", "translateme", "--language", "de", raises=True)
    assert "Unknown language 'de'" in error


def test_forwarding_pdb(qidoc_action):
    """ Test Forwarding Pdb """
    qidoc_action.add_test_project("world")
    with mock.patch("sphinx.main") as mock_main:
        mock_main.return_value = 0
        qidoc_action("build", "world", "--pdb")
        kwargs = mock_main.call_args[1]
        assert "-P" in kwargs["argv"]


def test_breathe(qidoc_action):
    """ Test Breathe """
    qidoc_action.add_test_project("libworld")
    qidoc_action.add_test_project("templates")
    world_breathe = qidoc_action.add_test_project("world-breathe")
    qidoc_action("build", "world-breathe")
    index_html = os.path.join(world_breathe.html_dir, "index.html")
    if six.PY3:
        with open(index_html, "r", encoding='utf-8') as fp:
            assert "the answer" in fp.read()
    else:
        with open(index_html, "r") as fp:
            assert "the answer" in fp.read().decode("utf-8")


def test_missing_deps(qidoc_action):
    """ Test Missing Deps """
    qidoc_action.add_test_project("hello")
    error = qidoc_action("build", "hello", raises=True)
    assert "world" in error
