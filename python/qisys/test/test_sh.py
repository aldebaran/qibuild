## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import stat
import pytest

import qisys.sh

def test_install_ro(tmpdir):
    tmp = tmpdir.strpath
    src = os.path.join(tmp, "src")
    os.mkdir(src)
    ro = os.path.join(src, "ro")
    with open(ro, "w") as fp:
        fp.write("ro\n")
    # 200:
    os.chmod(ro, stat.S_IRUSR)
    dest = os.path.join(tmp, "dest")
    qisys.sh.install(src, dest)

def test_install_on_self(tmpdir):
    a_file = tmpdir.join("a")
    a_file.write("")
    # pytlint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.sh.install(a_file.strpath, tmpdir.strpath)
    assert "are the same file" in e.value.message
    with pytest.raises(Exception) as e:
        qisys.sh.install(tmpdir.strpath, tmpdir.strpath)
    assert "are the same directory" in e.value.message

def test_is_path_inside():
   assert qisys.sh.is_path_inside("foo/bar", "foo")
   assert qisys.sh.is_path_inside("foo/bar", "foo/bar")
   assert qisys.sh.is_path_inside("foo", "foo/bar") is False
   assert qisys.sh.is_path_inside("lib/libfoobar", "lib/libfoo") is False
   assert qisys.sh.is_path_inside("gui/bar/libfoo", "lib") is False
