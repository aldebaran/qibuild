## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Automatic testing for handling archives

"""

import os
import stat

import pytest

import qisys

from qisys.archive import compress
from qisys.archive import extract
from qisys.archive import guess_algo


## zip does not support:
## - symlinks (they are dereferenced during the archive creation)
## - read-only directory


# def guess_algo(archive):
def test_guess_algo():
    extension = {
        'zip': ["zip"],
        'gzip': ["gz", "tgz", "tar.gz"],
        'bzip2': ["bz2", "tbz2", "tar.bz2"],
        'xz': ["xz", "tar.xz"],
        }
    basename  = ["archive",
                 "archive.{0}",
                 "/tmp.{0}/archive",
                 "/tmp.{0}/archive.{0}"]
    for algo, exts in extension.iteritems():
        for base_ in basename:
            for padding in extension.values():
                filename = base_.format(padding[0])
                for ext_ in exts:
                    filename += "." + ext_
                    res = guess_algo(filename)
                    assert res == algo
    for ext in ["tar", "Z", "tar.Z", "foo", "tar.foo"]:
        for base_ in basename:
            for padding in extension.values():
                filename = ".".join([base_.format(padding[0]), ext])
                res = guess_algo(filename)
                assert res == ext.rsplit(".", 1)[-1]
    return




def _test_compress_extract(tmpdir, algo, extension, compress_func, extract_func):
    ## Create the test archive
    srcdir   = tmpdir.mkdir("src")
    dstdir   = tmpdir.mkdir("dst")
    srcdir.mkdir("a")
    srcdir.join("a").join("1.txt").write("1")
    srcdir.join("a").join("2.txt").write("2")
    srcdir.mkdir("b")
    srcdir.join("b").join("3.txt").write("3")
    ## ... with symlinks
    srcdir.join("linkto_a").mksymlinkto("a")
    srcdir.join("linkto_b_3.txt").mksymlinkto("b/3.txt")
    srcdir.join("b").join("4.txt").mksymlinkto("3.txt")
    srcdir.join("b").join("linkto_a_from_b").mksymlinkto("../a")
    ## ... with ro file
    srcdir.mkdir("e")
    srcdir.join("e").join("ro_file.txt").write("ro-file")
    srcdir.join("e").join("ro_file.txt").chmod(0444)
    ## ... with ro dir
    srcdir.mkdir("ro_dir")
    srcdir.join("ro_dir").join("in_ro_dir.txt").write("ro-dir")
    srcdir.join("ro_dir").join("in_ro_dir.txt").chmod(0444)
    srcdir.join("ro_dir").chmod(0555)
    ## ... with executable
    srcdir.mkdir("bin")
    srcdir.join("bin").join("rw_bip").write("bip")
    srcdir.join("bin").join("rw_bip").chmod(0755)
    srcdir.join("bin").join("ro_bip").write("bop")
    srcdir.join("bin").join("ro_bip").chmod(0555)
    ## Pre-assert
    archive_base_ = tmpdir.join("arch").strpath
    archive_path_ = compress_func(srcdir.strpath, archive=archive_base_, algo=algo)
    extract_path_ = extract_func(archive_path_, dstdir.strpath, algo=algo)
    dstdir   = dstdir.join(os.path.basename(extract_path_))
    archpath = tmpdir.join(os.path.basename(archive_path_))
    src_ls_r = [x.strpath.split(srcdir.strpath + os.sep, 1)[-1] for x in srcdir.visit(sort=True)]
    dst_ls_r = [x.strpath.split(dstdir.strpath + os.sep, 1)[-1] for x in dstdir.visit(sort=True)]
    assert srcdir.join("linkto_a").check(exists=1, dir=1, link=1)
    assert srcdir.join("linkto_b_3.txt").check(exists=1, file=1, link=1)
    assert srcdir.join("b").join("linkto_a_from_b").check(exists=1, dir=1, link=1)
    assert srcdir.join("b").join("4.txt").check(exists=1, file=1, link=1)
    ## Tests
    ## archive existence
    assert archpath.strpath == archive_base_ + extension
    assert archpath.strpath == archive_path_
    print archive_path_
    assert archpath.check(exists=1, file=1, link=0)
    ## content
    assert dstdir.join("a").check(exists=1, dir=1, link=0)
    assert dstdir.join("a").join("1.txt").check(exists=1, file=1, link=0)
    assert dstdir.join("a").join("2.txt").check(exists=1, file=1, link=0)
    assert dstdir.join("b").check(exists=1, dir=1, link=0)
    assert dstdir.join("b").join("3.txt").check(exists=1, file=1, link=0)
    assert dstdir.join("e").check(exists=1, dir=1, link=0)
    assert dstdir.join("e").join("ro_file.txt").check(exists=1, file=1, link=0)
    assert dstdir.join("ro_dir").check(exists=1, dir=1, link=0)
    assert dstdir.join("ro_dir").join("in_ro_dir.txt").check(exists=1, file=1, link=0)
    assert dstdir.join("bin").check(exists=1, dir=1, link=0)
    assert dstdir.join("bin").join("rw_bip").check(exists=1, file=1, link=0)
    assert dstdir.join("bin").join("ro_bip").check(exists=1, file=1, link=0)
    print "src:"
    print "\n".join(["  %s" % x for x in src_ls_r])
    print "dst:"
    print "\n".join(["  %s" % x for x in dst_ls_r])
    if algo == "zip" and compress_func == compress:
        # Current implementation of qisys.archive.compress does not
        # dereference symlinks to directory, but just skip them. So:
        # - symlink to file become a file;
        # - symlink to directory is excluded from archiving.
        #
        # So, just remove all entry through a symlink directory from the
        # source file list.
        #
        # Note: Unlikely, zip binary dereference all symlinks:
        #       - symlink to file become a file;
        #       - symlink to directory become a directory;
        src_ls_r = [x for x in src_ls_r if not "linkto_a" in x]
    assert set(src_ls_r) == set(dst_ls_r)
    ## mode/permissions
    assert stat.S_IMODE(dstdir.join("e").join("ro_file.txt").stat().mode) == 0444
    assert stat.S_IMODE(dstdir.join("ro_dir").join("in_ro_dir.txt").stat().mode) == 0444
    if not algo == "zip" or not compress_func == compress:
        # Current implementation of qisys.archive.compress does not
        # support read-only directory.
        #
        # So, just skip the test.
        #
        # Note: Unlikely, zip binary keeps permissions on files and directories
        #       (see "zipinfo -l").
        assert stat.S_IMODE(dstdir.join("ro_dir").stat().mode) == 0555
    assert stat.S_IMODE(dstdir.join("bin").join("rw_bip").stat().mode) == 0755
    assert stat.S_IMODE(dstdir.join("bin").join("ro_bip").stat().mode) == 0555
    ## symlinks
    # Current implementation of qisys.archive.compress does not
    # dereference symlinks to directory, but just skip them. So:
    # - symlink to file become a file;
    # - symlink to directory is excluded from archiving.
    #
    # So, skip the sy;mlink-specific tests.
    #
    # Note: Unlikely, zip binary dereference all symlinks:
    #       - symlink to file become a file;
    #       - symlink to directory become a directory;
    assert dstdir.join("linkto_b_3.txt").check(exists=1)
    assert dstdir.join("linkto_b_3.txt").check(exists=1, file=1)
    if not algo == "zip":
        assert dstdir.join("linkto_b_3.txt").check(exists=1, file=1, link=1)
        assert dstdir.join("linkto_b_3.txt").readlink() == "b/3.txt"
    assert dstdir.join("b").join("4.txt").check(exists=1)
    assert dstdir.join("b").join("4.txt").check(exists=1, file=1)
    if not algo == "zip":
        assert dstdir.join("b").join("4.txt").check(exists=1, file=1, link=1)
        assert dstdir.join("b").join("4.txt").readlink() == "3.txt"
    if not algo == "zip" or not compress_func == compress:
        assert dstdir.join("linkto_a").check(exists=1)
        assert dstdir.join("linkto_a").check(exists=1, dir=1)
    if not algo == "zip":
        assert dstdir.join("linkto_a").check(exists=1, dir=1, link=1)
        assert dstdir.join("linkto_a").readlink() == "a"
    if not algo == "zip" or not compress_func == compress:
        assert dstdir.join("b").join("linkto_a_from_b").check(exists=1)
        assert dstdir.join("b").join("linkto_a_from_b").check(exists=1, dir=1)
    if not algo == "zip":
        assert dstdir.join("b").join("linkto_a_from_b").check(exists=1, dir=1, link=1)
        assert dstdir.join("b").join("linkto_a_from_b").readlink() == "../a"
    return


def extern_compress(directory, archive=None, algo="zip", quiet=False):
    if archive is None:
        archive = directory
    if algo == "zip":
        prog = "zip"
        if not archive.endswith(".zip"):
            archive += ".zip"
        cmd = ["-r", archive, os.path.basename(directory)]
        cwd = os.path.dirname(directory)
    else:
        prog = "tar"
        if algo == "tar" and not archive.endswith(".tar"):
            archive += ".tar"
        elif algo == "gzip" and not archive.endswith(".tar.gz"):
            archive += ".tar.gz"
        elif algo == "bzip2" and not archive.endswith(".tar.bz2"):
            archive += ".tar.bz2"
        elif algo == "xz" and not archive.endswith(".tar.xz"):
            archive += ".tar.xz"
        cmd = []
        if algo != "tar":
            cmd += ["--{0}".format(algo)]
        cmd += ["-cf", archive]
        cmd += ["-C", os.path.dirname(directory)]
        cmd += [os.path.basename(directory)]
        cwd = None
    cmd.insert(0, qisys.command.find_program(prog, raises=True))
    qisys.command.call(cmd, cwd=cwd)
    return archive

def extern_extract(archive, directory, algo="zip", quiet=False):
    if algo == "zip":
        prog = "unzip"
        cmd = ["-x", archive]
        cwd = directory
    else:
        prog = "tar"
        cmd = []
        if algo != "tar":
            cmd += ["--{0}".format(algo)]
        cmd += ["-xf", archive]
        cmd += ["-C", directory]
        cwd = None
    cmd.insert(0, qisys.command.find_program(prog, raises=True))
    qisys.command.call(cmd, cwd=cwd)
    if len(os.listdir(directory)) == 1:
        directory = os.path.join(directory, os.listdir(directory)[0])
    return directory


# pylint: disable-msg=E1101
@pytest.mark.parametrize(("algo", "extension", "compress_func", "extract_func"), [
        ("zip",   ".zip",     compress, extract),
        ("gzip",  ".tar.gz",  compress, extract),
        ("bzip2", ".tar.bz2", compress, extract),
        ("xz",    ".tar.xz",  compress, extract),
        ("tar",   ".tar",     compress, extract),

        ("zip",   ".zip",     extern_compress, extract),
        ("gzip",  ".tar.gz",  extern_compress, extract),
        ("bzip2", ".tar.bz2", extern_compress, extract),
        ("xz",    ".tar.xz",  extern_compress, extract),
        ("tar",   ".tar",     extern_compress, extract),

        ("zip",   ".zip",     compress, extern_extract),
        ("gzip",  ".tar.gz",  compress, extern_extract),
        ("bzip2", ".tar.bz2", compress, extern_extract),
        ("xz",    ".tar.xz",  compress, extern_extract),
        ("tar",   ".tar",     compress, extern_extract),
])
def test_compress_extract_valid(tmpdir, algo, extension, compress_func, extract_func):
    _test_compress_extract(tmpdir, algo, extension, compress_func, extract_func)
    return


# pylint: disable-msg=E1101
@pytest.mark.parametrize(("algo", "extension"), [
        ("foo", ".foo"),
        ("foo", ".tar.foo"),
])
def test_compress_extract_invalid(tmpdir, algo, extension):
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        _test_compress_extract(tmpdir, algo, extension, compress, extract)
    assert "Unknown algorithm: foo" in e.value.message
    assert "Known algorithms are"   in e.value.message

def test_compress_broken_symlink(tmpdir):
    src = tmpdir.mkdir("src")
    broken_symlink = os.symlink("/does/not/exist", src.join("broken").strpath)
    res = qisys.archive.compress(src.strpath, algo="zip")

def test_extract_invalid(tmpdir):
    srcdir   = tmpdir.mkdir("src")
    destdir = tmpdir.mkdir("dest")
    archive = srcdir.join("empty.tar.gz")
    archive.write("")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.archive.extract(archive.strpath, destdir.strpath)
    assert "tar failed" in e.value.message
