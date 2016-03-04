## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import qibuild.cmake.modules

def test_generates_cmake_module(tmpdir):
    tmpdir.ensure("foo/lib/libfoo.so", file=True)
    tmpdir.ensure("foo/lib/libbar.so", file=True)
    tmpdir.ensure("foo/include", dir=True)
    module = qibuild.cmake.modules.generate_cmake_module(tmpdir.join("foo").strpath,
                                                         "foo")
    expected_path = tmpdir.join("foo/share/cmake/foo/foo-config.cmake")
    assert module == expected_path.strpath
    contents = expected_path.read()
    print contents
    assert "lib/libfoo.so" in contents
    assert "lib/libbar.so" in contents
