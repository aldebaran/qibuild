#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2021 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" QiBuild """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisys.command


def check_gettext():
    """ Check GetText """
    gettext = qisys.command.find_program("xgettext", raises=False)
    if not gettext:
        return False
    return True


def test_install_confintl_files(qilinguist_action, tmpdir):
    """ Test Install ConfIntl Files """
    dest = tmpdir.join("dest")
    if not check_gettext():
        return
    trad = qilinguist_action.trad
    qilinguist_action("update", "--all")
    qilinguist_action.create_po(trad)
    qilinguist_action("release", "--all")
    qilinguist_action("install", "--all", dest.strpath)
    assert dest.join("share", "locale", "translate", ".confintl").check(file=True)
