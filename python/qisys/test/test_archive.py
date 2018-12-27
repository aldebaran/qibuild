#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Automatic testing for handling archives """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import zipfile
import pytest

import qisys
from qisys.archive import extract, guess_algo

# We don't use the stdlib for tar: it does not have
# all the features `tar` has and is slower, so all tar tests
# are disabled on Windows


def test_create_extract_zip_simple(tmpdir):
    """ Test Create Extract ZIP Simple """
    tmpdir.ensure("foo/a/b.txt", file=True)
    tmpdir.ensure("foo/c.txt", file=True)
    foo_zip = qisys.archive.compress(tmpdir.join("foo").strpath)
    assert foo_zip.endswith(".zip")
    dest = tmpdir.mkdir("dest")
    qisys.archive.extract(foo_zip, dest.strpath)
    assert tmpdir.join("dest", "foo", "a", "b.txt").check(file=True)
    assert tmpdir.join("dest", "foo", "c.txt").check(file=True)


def test_create_extract_tar_simple(tmpdir):
    """ Test Create Extract TAR Simple """
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
    """ Test Rewrite Top Dir BZ2 """
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


def test_compress_broken_symlink(tmpdir):
    """ Test Compare Broken SymLink """
    # Windows doesn't support symlink
    if os.name == 'nt':
        return
    src = tmpdir.mkdir("src")
    _broken_symlink = os.symlink("/does/not/exist", src.join("broken").strpath)  # pylint:disable=no-member
    _res = qisys.archive.compress(src.strpath, algo="zip")


def test_extract_invalid_empty(tmpdir):
    """ Test Extract Invalid Empty """
    if os.name == 'nt':
        return
    srcdir = tmpdir.mkdir("src")
    destdir = tmpdir.mkdir("dest")
    archive = srcdir.join("empty.tar.gz")
    archive.write("")
    with pytest.raises(Exception) as e:
        qisys.archive.extract(archive.strpath, destdir.strpath)
    assert "tar failed" in e.value.message


def test_extract_invalid_no_topdir(tmpdir):
    """ Test Extract Invalid No Top Dir """
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
    with pytest.raises(qisys.archive.InvalidArchive) as e:
        qisys.archive.extract(buggy_zip_path, dest.strpath)
    assert "same top dir" in str(e.value)


def test_flat(tmpdir):
    """ Test Flat """
    src = tmpdir.mkdir("src")
    src.ensure("lib", "libfoo.so", file=True)
    src.ensure("include", "foo.h", file=True)
    src.ensure("qipackage.xml", file=True)
    output = tmpdir.join("foo-0.1.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    dest = tmpdir.mkdir("dest").mkdir("foo")
    qisys.archive.extract(res, dest.strpath, strict_mode=False)
    assert dest.join("include", "foo.h").check(file=True)


def test_symlinks(tmpdir):
    """ Test Simlinks """
    src = tmpdir.mkdir("src")
    src.ensure("lib", "libfoo.so.42", file=True)
    src.join("lib", "libfoo.so").mksymlinkto("libfoo.so.42")
    output = tmpdir.join("foo.zip")
    res = qisys.archive.compress(src.strpath, output=output.strpath, flat=True)
    dest = tmpdir.mkdir("dest").mkdir("foo")
    qisys.archive.extract(res, dest.strpath)
    assert dest.join("lib", "libfoo.so").islink()


def test_returned_value_when_extracting_flat_package(tmpdir):
    """ Test Returned Value When Extracting Flat Package """
    src = tmpdir.mkdir("src")
    src.ensure("a", file=True)
    src.ensure("b", file=True)
    archive = qisys.archive.compress(src.strpath, flat=True)
    dest = tmpdir.mkdir("dest")
    res = qisys.archive.extract(archive, dest.strpath, strict_mode=False)
    assert res == dest.strpath
