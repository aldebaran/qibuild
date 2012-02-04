## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This module contains function to
manipulate archives.

We will always manipulate .tar.gz archives on UNIX,
and .zip on windows. (keeping it close to the more common
used format of the given platform)

All archives should have a unique top dir.
"""

import os
import sys
import copy
import posixpath
import logging
import operator
import tarfile
import zipfile

import qibuild



LOGGER = logging.getLogger("buildtool.archive")

class InvalidArchive(Exception):
    """Just a custom exception """
    def __init__(self, message):
        self._message = message
        Exception.__init__(self)

    def __str__(self):
        return self._message

def extract_tar(archive_path, dest_dir):
    """ Extract a .tar.gz archive

    :return: path to the extracted archive
             (dest_dir/topdir)

    """
    # Algorithm taken from tarfile.extractall():
    # First, extract everything directory in 700 mode,
    # then reverse-sort the order of the directory and
    # re-fix the permissions as they were in the original archive
    # We have to do this in case the archive contains something like:
    # src
    #   ro
    #     a
    # where ro is a read-only directory
    #
    # Obviously, creating ro1 first with the same permissions as
    # in the archive will prevent 'a' to be created.
    # See test_archive.py for relevant test.

    LOGGER.debug("Extracting %s to %s", archive_path, dest_dir)
    archive = tarfile.open(archive_path)
    members = archive.getmembers()
    size = len(members)
    res = None
    orig_topdir = members[0].name.split(posixpath.sep)[0]
    done = 0
    # Extract directories with a safe mode.
    directories = list()
    for tarinfo in members:
        member_top_dir = tarinfo.name.split(posixpath.sep)[0]
        if done != 0 and member_top_dir != orig_topdir:
            # something wrong: members do not have the
            # same basename
            mess  = "Invalid member %s in archive:\n" % tarinfo.name
            mess += "Every files sould be in the same top dir (%s != %s)" % \
                 (orig_topdir, member_top_dir)
            raise InvalidArchive(mess)
        if tarinfo.isdir():
            directories.append(tarinfo)
            tarinfo = copy.copy(tarinfo)
            tarinfo.mode = 0700
        archive.extract(tarinfo, dest_dir)
        done += 1
        if sys.stdout.isatty():
            percent = float(done) /size * 100
            sys.stdout.write("Done: %.0f%%\r" % percent)
            sys.stdout.flush()

    # Reverse sort directories.
    directories.sort(key=operator.attrgetter('name'))
    directories.reverse()

    # Set correct owner, mtime and filemode on directories.
    for tarinfo in directories:
        dirpath = os.path.join(dest_dir, tarinfo.name)
        try:
            archive.chown(tarinfo, dirpath)
            archive.utime(tarinfo, dirpath)
            archive.chmod(tarinfo, dirpath)
        except tarfile.ExtractError:
            raise

    archive.close()
    LOGGER.debug("%s extracted to %s", archive_path, dest_dir)
    res = os.path.join(dest_dir, orig_topdir)
    return res


def extract_zip(archive_path, dest_dir):
    """ Extract a zip archive
    :return: path to the extracted archive
             (dest_dir/topdir)

    """
    (dest_dir/topdir)
    dest_dir = qibuild.sh.to_native_path(dest_dir)
    LOGGER.debug("Extracting %s to %s", archive_path, dest_dir)
    archive = zipfile.ZipFile(archive_path)
    members = archive.infolist()
    # There is always the top dir as the first element of the archive
    # (or so we hope)
    orig_topdir = members[0].filename.split(posixpath.sep)[0]
    size = len(members)
    for (i, member) in enumerate(members):
        member_top_dir = member.filename.split(posixpath.sep)[0]
        if i != 0 and member_top_dir != orig_topdir:
            # something wrong: members do not have the
            # same basename
            mess  = "Invalid member %s in archive:\n" % member.filename
            mess += "Every files sould be in the same top dir (%s != %s)" % \
                 (orig_topdir, member_top_dir)
            raise InvalidArchive(mess)
        # By-pass buggy zipfile for python 2.6:
        if sys.version_info < (2, 7):
            if member.filename.endswith("/"):
                # upstream buggy code would create an empty filename
                # instead of a directory, thus preventing next members
                # to be extracted
                to_create = member.filename[:-1]
                posix_dest_dir = qibuild.sh.to_posix_path(dest_dir)
                to_create = posixpath.join(posix_dest_dir, to_create)
                qibuild.sh.mkdir(to_create, recursive=True)
                continue
        archive.extract(member, path=dest_dir)
        percent = float(i) / size * 100
        if sys.stdout.isatty():
            sys.stdout.write("Done: %.0f%%\r" % percent)
            sys.stdout.flush()
    archive.close()
    LOGGER.debug("%s extracted to %s", archive_path, dest_dir)
    res = os.path.join(dest_dir, orig_topdir)
    return res

def extract(archive_path, directory, topdir=None):
    """Extract an archive, calling extract_zip or extract_tar
    when necessary

    The top directory of the archive will be replaced by topdir
    if it is given

    :return: path to the extracted archive
    """
    if archive_path.endswith(".zip"):
        extract_fun = extract_zip
    else:
        extract_fun = extract_tar

    # Errors returned by tarfile of zipfile are not very good,
    # so let's just catch everything
    try:
        if topdir:
            with qibuild.sh.TempDir() as tmp:
                extracted = extract_fun(archive_path, tmp)
                dest = os.path.join(directory, topdir)
                qibuild.sh.install(extracted, dest, quiet=True)
                res = dest
        else:
            res = extract_fun(archive_path, directory)
        return res
    except Exception, err:
        mess = "Error occured when extracting %s\n" % archive_path
        mess += "Original error was: %s" % err
        raise InvalidArchive(mess)


def zip_win(directory):
    """Compress the directory in a .zip file

    """
    archive_name = directory + ".zip"
    # Convert to DOS path just to be sure:
    directory    = qibuild.sh.to_native_path(directory)
    archive_name = qibuild.sh.to_native_path(archive_name)
    archive = zipfile.ZipFile(archive_name, "w", zipfile.ZIP_DEFLATED)
    for (root, directories, filenames) in os.walk(directory):
        for filename in filenames:
            full_path = os.path.join(root, filename)
            rel_path = os.path.relpath(full_path, directory)
            arcname  = os.path.join(os.path.basename(directory), rel_path)
            archive.write(full_path, arcname)
    archive.close()
    return archive_name


def zip_unix(directory):
    """
    Call tar cvfz on a directory

    """
    # Do not use tarfile python module when tar:
    # - is faster
    # - is not buggy
    base_dir = os.path.basename(directory)
    work_dir = os.path.abspath(os.path.join(directory, ".."))
    base_archive_name = base_dir + ".tar.gz"
    cmd = ["tar", "cfz", base_archive_name, base_dir]
    qibuild.command.call(cmd, cwd=work_dir)
    full_archive_name = os.path.join(work_dir, base_archive_name)
    return full_archive_name

def zip( directory):
    """Zip a directory, using .tar.gz or .zip according to the current
    platform

    """
    if sys.platform.startswith("win"):
        return zip_win(directory)
    else:
        return zip_unix(directory)

def extracted_name(archive_name):
    """Return the extracted name from the archive name.

    Warning: this assumes the archive is well-formed
    (ie the root dir of foo.tar.gz is foo)

    >>> extracted_name("foo.zip")
    'foo'
    >>> extracted_name("foo.tar.gz")
    'foo'
    """
    known_exts = [".zip", ".tar.gz", ".tar.bz2"]
    for ext in known_exts:
        if archive_name.endswith(ext):
            return archive_name[:-len(ext)]

def archive_name(directory):
    """ Return the name an archive made from the
    directory would have.
    (platform-dependant)

    On windows::

      >>> archive_name('foo')
      foo.zip

    Elsewhere::

      >>> archive_name('foo')
      foo.tar.gz
    """
    if sys.platform.startswith("win"):
        return directory + ".zip"
    else:
        return directory + ".tar.gz"




if __name__ == "__main__":
    extract(sys.argv[1], sys.argv[2], topdir="py")
