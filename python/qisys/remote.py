#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
"""
Set of tools to perform remote operations,
downloading package or reading configs from URLs.
"""
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import os
import re
import io
import ftplib
import six

import qibuild.config
import qisys.sh
import qisys.command
from qisys import ui

if six.PY3:
    from urllib import parse as urlparse
    from urllib.request import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler,\
        build_opener, install_opener, urlopen
else:
    import urlparse
    from urllib2 import HTTPPasswordMgrWithDefaultRealm, HTTPBasicAuthHandler,\
        build_opener, install_opener, urlopen


def progress_callback(total, done):
    """ Called during download """
    qisys.ui.info_progress(done, total, "Done")


def get_server_access(server_name):
    """
    Get server access for a remote site.
    :param server: A :ref:`qibuild-xml-node-server` in
                   the global qibuild xml configuration file
    :return: A ``qibuild.config.Access`` instance
    """
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    access = qibuild_cfg.get_server_access(server_name)
    return access


def get_ftp_access(server_name):
    """
    Get ftp password from the config file
    :param server: A :ref:`qibuild-xml-node-server` in
                   the global qibuild xml configuration file
    :return: A ``qibuild.config.Access`` instance
    """
    access = get_server_access(server_name)
    if not access:
        return "anonymous", "anonymous", "/"
    return access.username, access.password, access.root


def authenticated_urlopen(location):
    """ A wrapper around urlopen adding authentication information if provided by the user. """
    passman = HTTPPasswordMgrWithDefaultRealm()
    server_name = urlparse.urlsplit(location).netloc
    access = get_server_access(server_name)
    if access is not None:
        user = access.username
        password = access.password
        if user is not None and password is not None:
            passman.add_password(None, location, user, password)
    authhandler = HTTPBasicAuthHandler(passman)
    opener = build_opener(authhandler)
    install_opener(opener)
    return urlopen(location)


def open_remote_location(location, timeout=10):
    """ Open a file from an url
    :return: a file-like object
    """
    url_split = urlparse.urlsplit(location)
    server_name = url_split.netloc
    if url_split.scheme == "ftp":
        (username, password, root) = get_ftp_access(server_name)
        ftp = ftplib.FTP(server_name, username, password, timeout=timeout)
        if root:
            ftp.cwd(root)

        class Transfer(object):
            """ Transfer Class """
            pass

        Transfer.data = ""
        # url_split.path has a trailing "/":
        cmd = "RETR " + url_split.path[1:]

        def retr_callback(data):
            """ Retr Callback """
            Transfer.data += data

        ftp.retrbinary(cmd, retr_callback)
        return io.StringIO(Transfer.data)
    else:
        return authenticated_urlopen(location)


def download(url, output_dir, output_name=None,
             callback=progress_callback, clobber=True, message=None):
    """
    Download a file from an url, and save it in output_dir.
    :param output_name: The name of the file will be the basename of the url,
        unless output_name is given
    :param callback: callback to use to show download progress.
        By default :py:func:`qisys.remote.callback` is called
    :param message: a list of arguments for :py:func:`qisys.ui.info`
        Will be printed right before the progress bar.
    :param clobber: If False, the file won't be overwritten if it
        already exists (True by default)
    :return: the path to the downloaded file
    """
    qisys.sh.mkdir(output_dir, recursive=True)
    if output_name:
        dest_name = os.path.join(output_dir, output_name)
    else:
        dest_name = url.split("/")[-1]
        dest_name = os.path.join(output_dir, dest_name)
    error = None
    if os.path.exists(dest_name) and not clobber:
        return dest_name
    if message:
        ui.info(*message)
    try:
        dest_file = open(dest_name, "wb")
    except Exception as e:
        mess = "Could not save %s to %s\n" % (url, dest_name)
        mess += "Error was %s" % e
        raise Exception(mess)
    url_split = urlparse.urlsplit(url)
    url_obj = None
    server_name = url_split.netloc
    try:
        if url_split.scheme == "ftp":
            # We cannot use urllib2 here because it has no support
            # for username/password for ftp, so we will use ftplib
            (username, password, root) = get_ftp_access(server_name)
            ftp = ftplib.FTP(server_name, username, password)
            if root:
                ftp.cwd(root)

            class Tranfert(object):
                """ Transfert Class """
                pass

            # Set binary mode
            ftp.voidcmd("TYPE I")
            size = ftp.size(url_split.path[1:])
            Tranfert.xferd = 0

            def retr_callback(data):
                """ Retr Callback """
                Tranfert.xferd += len(data)
                if callback:
                    callback(size, Tranfert.xferd)
                dest_file.write(data)

            cmd = "RETR " + url_split.path[1:]
            ftp.retrbinary(cmd, retr_callback)
        else:
            url_obj = authenticated_urlopen(url)
            if six.PY3:
                content_length = url_obj.headers.get('content-length')
            else:
                content_length = url_obj.headers.dict['content-length']
            size = int(content_length)
            buff_size = 100 * 1024
            xferd = 0
            while xferd < size:
                data = url_obj.read(buff_size)
                if not data:
                    break
                xferd += len(data)
                if callback:
                    callback(size, xferd)
                dest_file.write(data)
    except Exception as e:
        error = "Could not download file from %s\n to %s\n" % (url, dest_name)
        error += "Error was: %s" % e
    finally:
        dest_file.close()
        if url_obj:
            url_obj.close()
    if error:
        qisys.sh.rm(dest_name)
        raise Exception(error)
    return dest_name


def deploy(local_directory, remote_url, filelist=None):
    """ Deploy a local directory to a remote url. """
    # ensure destination directory exist before deploying data
    if not (remote_url.host and remote_url.remote_directory):
        message = "Remote URL is invalid; host and remote directory must be specified"
        raise Exception(message)
    user = "%s@" % remote_url.user if remote_url.user else ""
    cmd = ["ssh"]
    if remote_url.port:
        cmd.extend(["-p", str(remote_url.port)])
    cmd.extend(["%s%s" % (user, remote_url.host)])
    cmd.extend(["mkdir", "-p", remote_url.remote_directory])
    qisys.command.call(cmd)
    # This is required for rsync to do the right thing,
    # otherwise the basename of local_directory gets
    # created
    local_directory = local_directory + "/."
    cmd = ["rsync",
           "--recursive",
           "--links",
           "--perms",
           "--times",
           "--specials",
           "--progress",  # print a progress bar
           "--checksum",  # verify checksum instead of size and date
           "--exclude=.debug/"]
    if remote_url.port:
        cmd.extend(["-e", "ssh -p %d" % remote_url.port])
    if filelist:
        cmd.append("--files-from=%s" % filelist)
    cmd.append(local_directory)
    cmd.append("%s%s:%s" % (user, remote_url.host, remote_url.remote_directory))
    qisys.command.call(cmd)


class URLParseError(Exception):
    """ URLParseError Custom Exception """
    pass


class URL(object):
    """ URL Class """
    def __init__(self, url_as_string):
        self.as_string = url_as_string
        self.user = None
        self.host = None
        self.port = None
        self.remote_directory = None
        self._parse(url_as_string)

    def _parse(self, string):
        """ Parse an URL String """
        modern_scheme = r"""
ssh://
(?:
    (?P<user>[^@]+)
@)?       # user is anything but @, then the @ separator
(?P<host>[^:/]+)       # host is anything but : and /
(:(?P<port>\d+))?      # optional port
(/(?P<remote_dir>.*))? # optional remote directory
"""
        match = re.match(modern_scheme, string, re.VERBOSE)
        if match:
            self._handle_match(match)
        else:
            old_scheme = """
(?P<user>[^@]+)        # user is anything but @, and optional
@                      # mandatory @ separator
(?P<host>[^:/]+)       # host is anything but : and /
(
  (:|/)?               # directory separator is either : or /
  (?P<remote_dir>.*))? # remote directory is optional
        """
            match = re.match(old_scheme, string, re.VERBOSE)
            if match:
                self._handle_match(match)
            else:
                raise URLParseError(""" \
Could not parse %s as a valid url.
Supported schemes are

  user@host:directory

  ssh://user@host:port/directory
""" % self.as_string)

    def _handle_match(self, match):
        """ Handle Match """
        match_dict = match.groupdict()
        self.user = match_dict.get("user")
        self.host = match_dict["host"]
        self.port = 22
        if "port" in match_dict and match_dict["port"]:
            self.port = int(match_dict["port"])
        self.remote_directory = match_dict["remote_dir"] or None
