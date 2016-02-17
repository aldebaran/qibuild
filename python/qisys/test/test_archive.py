## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for handling archives

"""

import os
import sys
import stat
import zipfile

import pytest

import qisys

import qisys.error
from qisys.archive import compress
from qisys.archive import extract
from qisys.archive import guess_algo

from qisys.test.conftest import skip_on_win

# We don't use the stdlib for tar: it does not have
# all the features `tar` has and is slower, so all tar tests
# are disabled on Windows


def test_create_extract_zip_simple(tmpdir):
    tmpdir.ensure("foo/a/b.txt", file=True)
    tmpdir.ensure("foo/c.txt", file=True)
    foo_zip = qisys.archive.compress(tmpdir.join("foo").strpath)
    assert foo_zip.endswith(".zip")
    dest = tmpdir.mkdir("dest")
    qisys.archive.extract(foo_zip, dest.strpath)
    assert tmpdir.join("dest", "foo", "a", "b.txt").check(file=True)
    assert tmpdir.join("dest", "foo", "c.txt").check(file=True)

def test_create_extract_tar_simple(tmpdir):
    if os.name == 'nt':
        return
    tmpdir.ensure("foo/a/b.txt", file=True)
    tmpdir.ensure("foo/c.txt", file=True)
    foo_tar_gz = qisys.archive.compress(tmpdir.join("foo").strpath, algo="gzip")
    assert foo_tar_gz.endswith(".tar.gz")
    dest = tmpdir.mkdir("dest")
    # extract should guess the algo using the extension:
    qisys.archive.extract(foo_tar_gz, dest.strpath)
    assert tmpdir.join("dest", "foo", "a", "b.txt").check(file=True)
    assert tmpdir.join("dest", "foo", "c.txt").check(file=True)

def test_rewrite_top_dir_bz2(tmpdir):
    if os.name == 'nt':
        return
    # We need that when converting gentoo binary packages
    src = tmpdir.mkdir("src")
    src.ensure("usr/lib/libfoo.so", file=True)
    src.ensure("usr/include/foo/foo.h", file=True)
    cmd = ["tar", "--create", "--bzip2", "--file", "foo.tbz2", "./usr"]
    qisys.command.call(cmd, cwd=src.strpath)
    foo_tbz2 = src.join("foo.tbz2").strpath
    dest = tmpdir.mkdir("dest")
    qisys.archive.extract(foo_tbz2, dest.strpath)
    assert dest.join("foo/usr/lib/libfoo.so", file=True)
    assert dest.join("foo/usr/include/foo/foo.h", file=True)

@skip_on_win
def test_compress_broken_symlink(tmpdir):
    # Windows doesn't support symlink
    if os.name == 'nt':
        return
    src = tmpdir.mkdir("src")
    broken_symlink = os.symlink("/does/not/exist", src.join("broken").strpath)
    res = qisys.archive.compress(src.strpath, algo="zip")

# pylint: disable-msg=E1101
@pytest.mark.skipif(not sys.platform.startswith("linux"),
                    reason="Test only makes sense on linux")
def test_extract_invalid_empty(tmpdir):
    # tar is likely not in PATH on Windows, and on mac,
    # tar is perfectly happy with empty archives
    srcdir = tmpdir.mkdir("src")
    destdir = tmpdir.mkdir("dest")
    archive = srcdir.join("empty.tar.gz")
    archive.write("")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.error.Error) as e:
        qisys.archive.extract(archive.strpath, destdir.strpath)
    assert "tar failed" in e.value.message

# pylint: disable-msg=E1101
@pytest.mark.skipif(os.name == "nt",
                    reason="Does not work on Windows")
def test_extract_invalid_bad_tar(tmpdir):
    srcdir = tmpdir.mkdir("src")
    destdir = tmpdir.mkdir("dest")
    archive = srcdir.join("empty.tar.gz")
    archive.write("GARBAGE")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.archive.extract(archive.strpath, destdir.strpath)
    assert "tar failed" in e.value.message

def test_extract_invalid_no_topdir(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("superfluous.txt", file=True)
    src.ensure("foo/a.txt", file=True)
    src.ensure("foo/b.txt", file=True)
    buggy_zip_path = src.join("buggy.zip").strpath
    with qisys.sh.change_cwd(src.strpath):
        with zipfile.ZipFile(buggy_zip_path, "w") as archive:
            archive.write("superfluous.txt")
            archive.write("foo/a.txt")
            archive.write("foo/b.txt")

    dest = tmpdir.join("dest")
    # pylint: disable-msg=E1101
    with pytest.raises(qisys.archive.InvalidArchive) as e:
        qisys.archive.extract(buggy_zip_path, dest.strpath)
    assert "same top dir" in str(e.value)

def test_flat(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("lib", "libfoo.so", file=True)
    src.ensure("include", "foo.h", file=True)
    src.ensure("qipackage.xml", file=True)
    output = tmpdir.join("foo-0.1.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    dest = tmpdir.mkdir("dest").mkdir("foo")
    qisys.archive.extract(res, dest.strpath, strict_mode=False)
    assert dest.join("include", "foo.h").check(file=True)

@skip_on_win
def test_symlinks(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("lib", "libfoo.so.42", file=True)
    src.join("lib", "libfoo.so").mksymlinkto("libfoo.so.42")
    output = tmpdir.join("foo.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    dest = tmpdir.mkdir("dest").mkdir("foo")
    qisys.archive.extract(res, dest.strpath)
    assert dest.join("lib", "libfoo.so").islink()

@skip_on_win
def test_symlinks_created_with_zip(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("lib", "libfoo.so.42", file=True)
    src.join("lib", "libfoo.so").mksymlinkto("libfoo.so.42")
    output = tmpdir.join("foo.zip")
    cmd = ["zip", output.strpath,
          "--recurse-paths", ".",
          "--symlinks"]
    qisys.command.call(cmd, cwd=src.strpath)
    dest = tmpdir.mkdir("dest").mkdir("foo")
    qisys.archive.extract(output.strpath, dest.strpath)
    assert dest.join("lib", "libfoo.so").islink()

@skip_on_win
def test_symlink_already_here(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("lib", "libfoo.so.42", file=True)
    src.join("lib", "libfoo.so").mksymlinkto("libfoo.so.42")
    output = tmpdir.join("foo.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    dest = tmpdir.mkdir("dest").mkdir("foo")
    dest.ensure("lib", "libfoo.so", file=True)
    qisys.archive.extract(res, dest.strpath)
    assert dest.join("lib", "libfoo.so").islink()

def test_ro_file_already_here(tmpdir):
    src = tmpdir.mkdir("src")
    foo_src = src.ensure("foo.txt", file=True)
    foo_src.write("This is foo\n")
    dest = tmpdir.mkdir("dest")
    foo_dest = dest.ensure("foo.txt", file=True)
    foo_dest.chmod(000)
    output = tmpdir.join("foo.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    qisys.archive.extract(res, dest.strpath)
    assert foo_dest.read() == "This is foo\n"

def test_returned_value_when_extracting_flat_package(tmpdir):
    src = tmpdir.mkdir("src")
    src.ensure("a", file=True)
    src.ensure("b", file=True)
    archive = qisys.archive.compress(src.strpath, flat=True)
    dest = tmpdir.mkdir("dest")
    res = qisys.archive.extract(archive, dest.strpath, strict_mode=False)
    assert res == dest.strpath
