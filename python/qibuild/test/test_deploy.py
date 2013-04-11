## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


import pytest
import qisys.sh
import qibuild.deploy

def test_parse_url():
    res = qibuild.deploy.parse_url("john42-bar@foo.bar.com:some/really_strange-path")
    assert res == ("john42-bar@foo.bar.com", "foo.bar.com", "some/really_strange-path")
    res = qibuild.deploy.parse_url("john@foo:")
    assert res == ("john@foo", "foo", "")
    res = qibuild.deploy.parse_url("foo:lol")
    assert res == ("foo", "foo", "lol")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception):
        qibuild.deploy.parse_url("john@bar")
    with pytest.raises(Exception):
        qibuild.deploy.parse_url("john@bar:lol ")
