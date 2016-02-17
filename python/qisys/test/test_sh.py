## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import stat
import sys
import pytest

import qisys.error
import qisys.sh

from qisys.test.conftest import skip_on_win
from qisrc.test.conftest import TestGit

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
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qisys.sh.install(a_file.strpath, tmpdir.strpath)
    assert "are the same file" in e.value.message
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qisys.sh.install(tmpdir.strpath, tmpdir.strpath)
    assert "are the same directory" in e.value.message

@skip_on_win
def test_install_symlink(tmpdir):
   src = tmpdir.mkdir("src")
   a = src.ensure("a", file=True)
   b = src.join("b")
   b.mksymlinkto("a")
   dest = tmpdir.mkdir("dest")
   a_dest = dest.join("a")
   b_dest = dest.join("b")
   qisys.sh.install(b.strpath, b_dest.strpath)
   # Also install a so that b is not a broken symlink
   qisys.sh.install(a.strpath, a_dest.strpath)
   assert b_dest.check(file=True)
   assert b_dest.islink()
   assert b_dest.readlink() == "a"

def test_filter_hidden(tmpdir):
    src = tmpdir.ensure("src", dir=True)
    src.join("a_file").ensure(file=True)
    src.join(".hidden").ensure(file=True)
    dest = tmpdir.join("dest")
    def non_hidden(src):
        return not src.startswith(".")
    installed = qisys.sh.install(src.strpath, dest.strpath, filter_fun=non_hidden)
    a_file = dest.join("a_file")
    assert a_file.check(file=True)
    assert not dest.join(".hidden").check(file=True)
    assert installed == ["a_file"]

def test_ls_r_default(tmpdir):
    src = tmpdir.ensure("src", dir=True)
    src.join("a_file").ensure(file=True)
    src.join(".hidden").ensure(file=True)
    src.join("b/b_file").ensure(file=True)
    src.join("b/.b_file.swp").ensure(file=True)
    res = qisys.sh.ls_r(src.strpath)
    assert res == ["a_file", "b/b_file"]

def test_ls_r_all(tmpdir):
    src = tmpdir.join("src")
    src.ensure(".git/objects/0abc4", file=True)
    src.ensure(".a.txt.swp", file=True)
    src.ensure("a.txt", file=True)
    src.ensure("bar/baz.txt", file=True)
    src.ensure("baz/.baz.txt.swp", file=True)
    res = qisys.sh.ls_r(src.strpath)
    assert res == ["a.txt", "bar/baz.txt"]
    res = qisys.sh.ls_r(src.strpath, all=True)
    assert res == [
        ".a.txt.swp",
        ".git/objects/0abc4",
        "a.txt",
        "bar/baz.txt",
        "baz/.baz.txt.swp",
    ]

def test_iter_directory(tmpdir):
    src = tmpdir.ensure("src", dir=True)
    src.join("a_file").ensure(file=True)
    src.join(".hidden").ensure(file=True)
    src.join("b/b_file").ensure(file=True)
    src.join("b/.b_file.swp").ensure(file=True)
    res = sorted(qisys.sh.iter_directory(src.strpath, all=True))
    assert res == [".hidden", "a_file", "b/.b_file.swp", "b/b_file"]
    res = sorted(qisys.sh.iter_directory(src.strpath))
    assert res == ["a_file", "b/b_file"]

def test_is_path_inside():
   assert qisys.sh.is_path_inside(os.path.join("foo", "bar"), "foo")
   assert qisys.sh.is_path_inside(os.path.join("foo", "bar"),
                                  os.path.join("foo", "bar"))
   assert qisys.sh.is_path_inside("foo", os.path.join("foo", "bar")) is False
   assert qisys.sh.is_path_inside(os.path.join("lib", "libfoobar"),
                                  os.path.join("lib", "libfoo")) is False
   assert qisys.sh.is_path_inside(os.path.join("gui", "bar", "libfoo"),
                                  "lib") is False

def test_copy_git_src(tmpdir):
    src = tmpdir.mkdir("src")
    dest = tmpdir.mkdir("dest")
    foo_src = src.mkdir("foo")
    foo_git = TestGit(foo_src.strpath)
    foo_git.initialize()
    foo_git.commit_file("a.txt", "a\n")
    foo_git.commit_file("b.txt", "a\n")
    foo_src.ensure("c.txt", file=True)
    qisys.sh.copy_git_src(foo_src.strpath, dest.strpath)
    assert dest.join("a.txt").check(file=True)
    assert not dest.join("c.txt").check(file=True)

def test_is_runtime():
    def make_path(*parts):
        return os.path.join(*parts)
    assert qisys.sh.is_runtime(make_path("lib", "libfoo.a")) is False
    assert qisys.sh.is_runtime(make_path("include", "foo.h")) is False
    assert qisys.sh.is_runtime(make_path("lib", "python2.7", "Makefile")) is True
    assert qisys.sh.is_runtime(make_path("lib", "python2.7", "config", "pyconfig.h")) is True
    assert qisys.sh.is_runtime(make_path("include", "python2.7", "pyconfig.h")) is True
    if sys.platform == "darwin":
        assert qisys.sh.is_runtime("lib/libfoo.dylib") is True
    assert qisys.sh.is_runtime(make_path("lib", "fonts", "Vera.ttf")) is True

def test_install_return_value(tmpdir):
    src = tmpdir.mkdir("src")
    b = src.ensure("a", "b", file=True)
    d = src.ensure("a", "c", "d", file=True)
    dest = tmpdir.mkdir("dest")
    ret = qisys.sh.install(src.strpath, dest.strpath)
    assert ret == ["a/b", "a/c/d"]
    ret = qisys.sh.install(d.strpath, dest.strpath)
    assert ret == ["d"]

@skip_on_win
def test_install_qt_symlinks(tmpdir):
    tc_path = tmpdir.mkdir("toolchain")
    qt_src = tc_path.mkdir("qt")
    qt_src.ensure("lib", "QtCore.framework", "QtCore", file=True)
    qt_src.join("QtCore.framework").mksymlinkto("lib/QtCore.framework")
    dest = tmpdir.join("dest")
    qisys.sh.install(qt_src.strpath, dest.strpath, filter_fun=qisys.sh.is_runtime)
    assert dest.join("QtCore.framework").islink()

def test_to_posix_path():
   assert qisys.sh.to_posix_path(r"c:\foo\bar") ==  "c:/foo/bar"
   assert qisys.sh.to_posix_path(r"foo//bar") == "foo/bar"
   assert qisys.sh.to_posix_path(r"c:\foo\bar", fix_drive=True) == "/c/foo/bar"
