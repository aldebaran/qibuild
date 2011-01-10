"""This module contains various useful
functions to deal with FTP download/upload

"""

import os
import re
import sys
import posixpath
import logging
import ftplib

LOGGER = logging.getLogger("buildtool.ftp")


class FtpException(Exception):
    """Custon exception """
    # the ones from ftplib are not great ...
    def __init__(self, *args):
        FtpException.__init__(self, *args)


class FtpConnection:
    """A class to be used in a with statement.

    """
    def __init__(self, url, username="anonymous", password="anonymous", root=None):
        self.url = url
        self.username = username
        if root is None:
            root = "/"
        self.root = root
        self.password = password
        # The ftplib.FTP object:
        self._ftp = None

    def __enter__(self):
        """Open the ftp connection

        """
        self._ftp = ftplib.FTP(self.url, self.username, self.password)
        self._ftp.cwd(self.root)
        return self

    def __exit__(self, *unused_):
        """Close the ftp connection """
        if not self._ftp:
            return
        # Some FTP servers do not implement quit correctly.
        # If they don't, we have no choice but ignore the
        # error and close the connection anyway....
        try:
            self._ftp.quit()
        except ftplib.Error:
            pass
        self._ftp.close()

    def ftp_command(func):
        """Decorator for ftp functions.

        Make sure that:
        - CWD is correct.
        - Class was used with a "with" statement

        """
        def res(self, *args, **kwargs):
            # If self._ftp is None, we did not call __enter__,
            # so we are likely to not have use the with statement.
            # In this case, self._ftp is None, so just raise
            if self._ftp is None:
                raise Exception("You must use FtpConnection with a _with_ statement!")

            self._ftp.cwd("/")
            self._ftp.cwd(self.root)
            return func(self, *args, **kwargs)

        return res


    @ftp_command
    def ls(self, *args):
        return self._ftp.nlst(*args)

    @ftp_command
    def move_regexp(self, src, dest, regexp):
        """ move files matching regexp from src to dest
            dest is relative to src
        """
        pattern = re.compile(regexp)
        LOGGER.info("trying to move old versions to %s/%s", src, dest)
        self._ftp.cwd(src)
        try:
            self._ftp.mkd(dest)
        except ftplib.error_perm:
            pass
        flist = self._ftp.nlst()
        for f in flist:
            if pattern.match(f):
                LOGGER.info("moving %s to %s", f, dest)
                self._ftp.rename(f, "%s/%s" % (dest, f))

    @ftp_command
    def makedirs(self, folder):
        """Create directories.

        This is basically make mkdir -p made at the root of the FTP.

        The folder argument must be a canonic POSIX relative path
        to the root of the FtpConnection
        """
        LOGGER.debug("ftp: creating dir: %s", folder)
        subfolders = folder.split("/")
        # For each subfolder in the folders to create,
        # try to change the working dir.
        # If this fails, create the subfolder and continue.
        for subfolder in subfolders:
            try:
                self._ftp.cwd(subfolder)
            except ftplib.error_perm:
                self._ftp.mkd(subfolder)
                self._ftp.cwd(subfolder)

    @ftp_command
    def upload_files(self, files_to_upload, remote_directory):
        """Upload files using ftp.

        Note1: the remote_directory is always created using
        create_dest_dir

        Note2: the remote_directory should be a
        *relative POSIX PATH*

        """
        LOGGER.info("uploading %s to %s", ", ".join(files_to_upload), remote_directory)
        self.makedirs(remote_directory)
        # HACK: I got a permision denide if I remove this line.
        # Why ?
        self.ls()
        for filename in files_to_upload:
            if not os.path.exists(filename):
                raise Exception("This file does not exists: %s" % (filename))
            with open(filename, "rb") as file_object:
                basename = os.path.basename(filename)
                remote_path = posixpath.join(remote_directory, basename)
                cmd = "STOR %s" % remote_path
                LOGGER.debug("ftp: calling %s", cmd)
                self._ftp.storbinary(cmd, file_object)

    @ftp_command
    def parse_listing(self, subdir, regexpes):
        """Get the urls of several files on the server using a list of regexpes.

        Return a list of tuples (url, size)

        The length of the list maybe different that the lenght of the list
        of regexpes given as parameter.

        """
        urls = list()

        # Stupid callback because API of retrlines
        # sucks...
        lines = list()
        def store_line(line):
            lines.append(line)

        self._ftp.retrlines("LIST " + subdir, store_line)
        for line in lines:
            for regexp in regexpes:
                size = line.split()[4]
                name = line.split()[-1]
                match = re.match(regexp, name)
                if match is None:
                    continue
                full_url = posixpath.join(subdir, name)
                urls.append((full_url, size))
        return urls


    @ftp_command
    def get_latest_version(self, base_version):
        """Base version should be a string linke "1.8.x"
        Find the latest version available from the base_version
        subfolder
        """
        subdir = "v" + base_version
        filenames = self.ls(subdir)
        latest = -1
        for filename in filenames:
            version = filename.split()[-1]
            try:
                minor = int(version.split(".")[-1])
            except ValueError:
                continue
            if minor > latest:
                latest = minor
        splitted = base_version.split(".")
        splitted[-1] = str(latest)
        return ".".join(splitted)


    @ftp_command
    def download(self, subdir, regexpes, verbose=True, output_dir=None,
        allow_overwrite=False):
        """Retrieve files from a the server.

        Example:

            names = ["foo-\d{2}", "bar-.*"]
            with FtpConnection("user", "p4ssw0rd") as ftp:
                results = ftp.download("subdir", names. output_dir="spam/eggs")

        If this works, results looks like
        ["spam/eggs/foo-42",
         "spam/eggs/bar-1.42"]

        If allow_overwrite is True, file will be overwritten if it already exists,
        if not, we will simply skip the download.

        """
        if output_dir is None:
            output_dir = os.getcwd()
        urls = self.parse_listing(subdir, regexpes)
        res = list()

        for (url, size) in urls:
            base_name = posixpath.basename(url)
            dest_name = os.path.join(output_dir, base_name)
            if os.path.exists(dest_name) and not allow_overwrite:
                res.append(dest_name)
                continue
            dest_file = open(dest_name, "wb")
            if verbose:
                print "Downloading: ", url
            # We have to use class here
            # otherwise, with:
            """
            xfered = 0
            def retr_callback(data):
                xfered += len(data)

            you'll get: xfered: referenced variable before
            assignement.

            """
            class Tranfert:
                pass
            Tranfert.xfered = 0
            def retr_callback(data):
                dest_file.write(data)
                Tranfert.xfered += len(data)
                done = float(Tranfert.xfered) / float(size) * 100
                if verbose:
                    sys.stdout.write("Done: %.0f%%\r" % done)
                    sys.stdout.flush()
            cmd = "RETR " + url
            self._ftp.retrbinary(cmd, retr_callback)
            dest_file.close()
            res.append(dest_name)

        return res


def main():
    """Quick example of use """
    with FtpConnection("ananas") as ftp:
        #results = ftp.download("continuous/linux/", ["pldp.*"])
        #for res in results:
            #print res
        print ftp.get_latest_version("1.10.x")


if __name__ == "__main__":
    main()
