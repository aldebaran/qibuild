## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os

def test_install(qipy_action, tmpdir):
    big_project = qipy_action.add_test_project("big_project")
    dest = tmpdir.join("dest")
    qipy_action("install", "big_project", dest.strpath)
    site_packages = dest.join("lib", "python2.7", "site-packages")
    assert site_packages.join("spam.py").check(file=True)
    assert site_packages.join("foo", "bar", "baz.py").check(file=True)
    assert dest.join("bin", "script.py").check(file=True)

def test_install_with_distutils(qipy_action, tmpdir):
    with_distutils = qipy_action.add_test_project("with_distutils")
    dest = tmpdir.join("dest")
    qipy_action("bootstrap")
    qipy_action("install", "foo", dest.strpath)
    if os.name == "nt":
        foo_path = dest.join("Scripts", "foo.exe")
    else:
        foo_path = dest.join("bin", "foo")
    assert foo_path.check(file=True)

def test_empty_install(qipy_action, tmpdir):
    empty = qipy_action.add_test_project("empty")
    dest = tmpdir.join("dest")
    qipy_action("bootstrap")
    error = qipy_action("install", "empty", dest.strpath, raises=True)
    assert "Could not find anything to install" in error
