## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" test qibuild init """

import qisys.error
import qisys.script

import pytest


def test_works_from_an_empty_dir(tmpdir, monkeypatch):
    ''' positive test '''
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qibuild.actions.init")
    assert tmpdir.join(".qi").check(dir=True)


def test_fails_if_qi_dir(tmpdir, monkeypatch, record_messages):
    ''' negative test '''
    tmpdir.mkdir(".qi")
    monkeypatch.chdir(tmpdir)
    # pylint: disable-msg=E1101
    with pytest.raises(SystemExit) as err:
        qisys.script.run_action("qibuild.actions.init")
    assert err.value.code != 0
    assert record_messages.find(".qi directory")
