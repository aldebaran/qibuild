## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.command

def check_gettext():
    gettext = qisys.command.find_program("xgettext", raises=False)
    if not gettext:
        return False
    return True

def test_install_confintl_files(qilinguist_action, tmpdir):
    dest = tmpdir.join("dest")
    if not check_gettext():
        return
    trad = qilinguist_action.trad
    qilinguist_action("update", "--all")
    qilinguist_action.create_po(trad)
    qilinguist_action("release", "--all")
    qilinguist_action("install", "--all", dest.strpath)
    assert dest.join("share", "locale", "translate", ".confintl").check(file=True)
