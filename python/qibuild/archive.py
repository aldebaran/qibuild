## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""This module contains function to
manipulate archives.

We will always manipulate .tar.gz archives on UNIX,
and .zip on windows. (keeping it close to the more common
used format of the given platform)
"""

import os
import posixpath
import sys
import logging
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
    """Extract a .tar.gz archive"""
    LOGGER.debug("Extracting %s to %s", archive_path, dest_dir)
    archive = tarfile.open(archive_path)
    members = archive.getmembers()
    size = len(members)
    res = None
    topdir = members[0].name.split(posixpath.sep)[0]
    for (i, member) in enumerate(members):
        member_top_dir = member.name.split(posixpath.sep)[0]
        if i != 0 and topdir != member_top_dir:
            # something wrong: members do not have the
            # same basename
            mess  = "Invalid member %s in archive:\n" % member.name
            mess += "Every files sould be in the same top dir (%s != %s)" % \
                 (topdir, member_top_dir)
            raise InvalidArchive(mess)

        # Do not use archive.extract(member)
        # See: http://docs.python.org/library/tarfile.html#tarfile.TarFile.extract
        archive.extractall(members=[member], path=dest_dir)
        percent = float(i) / size * 100
        if sys.stdout.isatty():
            sys.stdout.write("Done: %.0f%%\r" % percent)
            sys.stdout.flush()
    archive.close()
    LOGGER.debug("%s extracted to %s", archive_path, dest_dir)
    res = os.path.join(dest_dir, topdir)
    return res


def extract_zip(archive_path, dest_dir):
    """Extract a zip archive"""
    LOGGER.debug("Extracting %s to %s", archive_path, dest_dir)
    archive = zipfile.ZipFile(archive_path)
    members = archive.infolist()
    # There is always the top dir as the first element of the archive
    # (or so we hope)
    topdir = members[0].filename.split(posixpath.sep)[0]
    size = len(members)
    for (i, member) in enumerate(members):
        member_top_dir = member.filename.split(posixpath.sep)[0]
        if i != 0 and topdir != member_top_dir:
            # something wrong: members do not have the
            # same basename
            mess  = "Invalid member %s in archive:\n" % member.filename
            mess += "Every files sould be in the same top dir (%s != %s)" % \
                 (topdir, member_top_dir)
            raise InvalidArchive(mess)
        archive.extract(member, path=dest_dir)
        percent = float(i) / size * 100
        if sys.stdout.isatty():
            sys.stdout.write("Done: %.0f%%\r" % percent)
            sys.stdout.flush()
    archive.close()
    LOGGER.debug("%s extracted to %s", archive_path, dest_dir)
    res = os.path.join(dest_dir, topdir)
    return res

def extract(archive_path, directory):
    """Extract an archive, calling extract_zip or extract_tar
    when necessary

    """
    try:
        if archive_path.endswith(".zip"):
            return extract_zip(archive_path, directory)
        else:
            return extract_tar(archive_path, directory)
    # Errors returned by tarfile of zipfile are not very good,
    # so let's just catch everything
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

    On windows:
        >> archive_name('foo')
        foo.zip
    Elsewhere:
        >> archive_name('foo')
        foo.tar.gz
    """
    if sys.platform.startswith("win"):
        return directory + ".zip"
    else:
        return directory + ".tar.gz"




if __name__ == "__main__":
    import doctest
    doctest.testmod()
