## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import stat

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

def test_is_path_inside():
   assert qisys.sh.is_path_inside("foo/bar", "foo")
   assert qisys.sh.is_path_inside("foo/bar", "foo/bar")
   assert qisys.sh.is_path_inside("foo", "foo/bar") is False
   assert qisys.sh.is_path_inside("lib/libfoobar", "lib/libfoo") is False
   assert qisys.sh.is_path_inside("gui/bar/libfoo", "lib") is False
