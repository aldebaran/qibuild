## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qitoolchain.feed import *

import pytest

def test_is_url():
    assert not is_url(r"c:\foo\bar" )
    assert is_url("http://foo.com/bar.xml")
    assert is_url("ftp://foo.com.bar.xml")

def test_parse_non_exising_path():
    #pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        tree_from_feed("does/not/exists")
    assert "not an existing path" in e.value.message
    assert "nor an url" in e.value.message
