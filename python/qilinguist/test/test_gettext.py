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
import subprocess

import qisys.command


WRONG_TRANSLATION = "Wrong translation :\n\n{}\nnot in\n\n{}"


def check_gettext():
    """ Check GetText """
    gettext = qisys.command.find_program("xgettext", raises=False)
    if not gettext:
        return False
    return True


def test_update(qilinguist_action):
    """ Test Update """
    if not check_gettext():
        return
    trad = qilinguist_action.trad
    fr_FR_po_file = os.path.join(trad.path, "po", "fr_FR.po")
    en_US_po_file = os.path.join(trad.path, "po", "en_US.po")
    pot_file = os.path.join(trad.path, "po", "translate.pot")
    assert not os.path.exists(fr_FR_po_file)
    assert not os.path.exists(en_US_po_file)
    assert not os.path.exists(pot_file)
    qilinguist_action("update", "translate")
    assert os.path.exists(fr_FR_po_file)
    assert os.path.exists(en_US_po_file)
    assert os.path.exists(pot_file)


def test_release(qilinguist_action):
    """ Test Release """
    if not check_gettext():
        return
    trad = qilinguist_action.trad
    fr_FR_mo_file = os.path.join(trad.path, "po", "share", "locale", "translate",
                                 "fr_FR", "LC_MESSAGES", "translate.mo")
    en_US_mo_file = os.path.join(trad.path, "po", "share", "locale", "translate",
                                 "fr_FR", "LC_MESSAGES", "translate.mo")
    assert not os.path.exists(fr_FR_mo_file)
    assert not os.path.exists(en_US_mo_file)
    qilinguist_action("update", "translate")
    qilinguist_action.create_po(trad)
    qilinguist_action("release", "translate")
    assert os.path.exists(fr_FR_mo_file)
    assert os.path.exists(en_US_mo_file)


def test_cplusplus_sdk_workflow(qilinguist_action):
    """ Test Cpp SDK Workflow """
    if not check_gettext():
        return
    trad = qilinguist_action.trad
    qilinguist_action.create_po(trad)
    qilinguist_action("update", "translate")
    qilinguist_action("release", "translate")
    trad.configure()
    trad.build()
    # check binary output
    binary = os.path.join(trad.sdk_directory, "bin", "translate")
    dictPath = os.path.join(trad.path, "po", "share", "locale", "translate")
    env = os.environ.copy()
    env["LANGUAGE"] = "fr_FR.UTF-8"  # for Ubuntu
    env["LC_ALL"] = "fr_FR.UTF-8"  # for Arch Linux
    cmd = [binary, dictPath]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_fr = b"""Bonjour, mon nom est NAO.
O\xc3\xb9 est Brian ?
Brian est dans la cuisine.
"""
    if out_fr not in out:
        pytest.fail(WRONG_TRANSLATION.format(out_fr.decode("utf-8"), out.decode("utf-8")))
    env = os.environ.copy()
    env["LANGUAGE"] = "en_US.UTF-8"
    cmd = [binary, dictPath]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_en = b"""Hi, my name is NAO.
Where is Brian?
Brian is in the kitchen.
"""
    if out_en not in out:
        pytest.fail(WRONG_TRANSLATION.format(out_en.decode("utf-8"), out.decode("utf-8")))


def test_cplusplus_install_workflow(qilinguist_action, tmpdir):
    """ Test Cpp Install Workflow """
    if not check_gettext():
        return
    trad = qilinguist_action.trad
    qilinguist_action.create_po(trad)
    qilinguist_action("update", "translate")
    qilinguist_action("release", "translate")
    trad.configure()
    trad.build()
    trad.install(tmpdir.strpath)
    # check mo files
    fr_mo_file = tmpdir.join("share", "locale", "translate", "fr_FR", "LC_MESSAGES", "translate.mo").strpath
    en_mo_file = tmpdir.join("share", "locale", "translate", "en_US", "LC_MESSAGES", "translate.mo").strpath
    assert os.path.exists(fr_mo_file)
    assert os.path.exists(en_mo_file)
    # check binary output
    binary = tmpdir.join("bin", "translate").strpath
    dict_path = tmpdir.join("share", "locale", "translate").strpath
    env = os.environ.copy()
    env["LANGUAGE"] = "fr_FR.UTF-8"  # for Ubuntu
    env["LC_ALL"] = "fr_FR.UTF-8"  # for Arch Linux
    cmd = [binary, dict_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_fr = b"""Bonjour, mon nom est NAO.
O\xc3\xb9 est Brian ?
Brian est dans la cuisine.
"""
    if out_fr not in out:
        pytest.fail(WRONG_TRANSLATION.format(out_fr.decode("utf-8"), out.decode("utf-8")))
    env = os.environ.copy()
    env["LANGUAGE"] = "en_US.UTF-8"
    cmd = [binary, dict_path]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE, env=env)
    out, _ = process.communicate()
    out_en = b"""Hi, my name is NAO.
Where is Brian?
Brian is in the kitchen.
"""
    if out_en not in out:
        pytest.fail(WRONG_TRANSLATION.format(out_en.decode("utf-8"), out.decode("utf-8")))
