## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import platform

import qibuild.find
from qibuild.find import library_name
from qibuild.find import binary_name

import pytest

def test_library_name():
    assert library_name("foo", debug=False, shared=True,  os_name="Windows") == "foo.dll"
    assert library_name("foo", debug=True,  shared=True,  os_name="Windows") == "foo_d.dll"
    assert library_name("foo", debug=False, shared=False, os_name="Windows") == "foo.lib"
    assert library_name("foo", debug=True,  shared=False, os_name="Windows") == "foo_d.lib"

    assert library_name("foo", shared=True,  os_name="Linux") == "libfoo.so"
    assert library_name("foo", shared=False, os_name="Linux") == "libfoo.a"

    assert library_name("foo", shared=True,  os_name="Darwin") == "libfoo.dylib"
    assert library_name("foo", shared=False, os_name="Darwin") == "libfoo.a"


def test_binary_name():
    assert binary_name("foo", debug=False, os_name="Windows") == "foo.exe"
    assert binary_name("foo", debug=True,  os_name="Windows") == "foo_d.exe"

    assert binary_name("foo", os_name="Darwin") == "foo"
    assert binary_name("foo", os_name="Linux") == "foo"


def test_expect_one(tmpdir):
    # No point in testing this on other OS, it's the same code
    if platform.system() != 'Linux':
        return
    a_path = tmpdir.mkdir("a")
    a_path.ensure("lib/libfoo.so", file=True)
    b_path = tmpdir.mkdir("b")
    b_path.ensure("bin/foo", file=True)

    res = qibuild.find.find([a_path.strpath, b_path.strpath], "foo",
                           expect_one=False)
    assert len(res) == 2

    # pylint: disable-msg=E1101
    with pytest.raises(qibuild.find.MultipleFound) as e:
        qibuild.find.find([a_path.strpath, b_path.strpath], "foo",
                                expect_one=True)

    with pytest.raises(qibuild.find.NotFound) as e:
        qibuild.find.find([a_path.strpath, b_path.strpath], "bar",
                                expect_one=True)

    res = qibuild.find.find_bin([b_path.strpath], "foo", expect_one=True)
    assert os.path.exists(res)
