## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qisys.command

from qilinguist.test.conftest import skip_no_gettext

@skip_no_gettext
def test_install_confintl_files(qilinguist_action, tmpdir):
    dest = tmpdir.join("dest")
    trad = qilinguist_action.trad
    qilinguist_action("update", "--all")
    qilinguist_action.create_po(trad)
    qilinguist_action("release", "--all")
    qilinguist_action("install", "--all", dest.strpath)
    assert dest.join("share", "locale", "translate", ".confintl").check(file=True)
