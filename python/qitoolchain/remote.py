## Copyright (C) 2011 Aldebaran Robotics

""" Set of tools to perform remote operations,
downloading package or reading configs from URLs

"""

import os
import sys
import ftplib
import urlparse
import urllib2
import logging
import ConfigParser
import StringIO

import qibuild

LOGGER = logging.getLogger(__name__)

REMOTE_CFG = "~/.config/qi/remote.cfg"

def callback(total, done):
    """ Called during download """
    if not sys.stdout.isatty():
        return
    percent = done * 100 / total
    sys.stdout.write("Done: %i%%\r" % percent)
    sys.stdout.flush()


def get_ftp_password(server):
    """ Get ftp password from the config file

    """
    remote_cfg = qibuild.sh.to_native_path(REMOTE_CFG)
    config = ConfigParser.ConfigParser()
    config.read(remote_cfg)
    if not config.has_section(server):
        return ("anonymous", "anonymous", "/")

    items = dict(config.items(server))

    return (
        items.get("username"),
        items.get("password"),
        items.get("root")
    )

def open_remote_location(location):
    """ Open a file from an url
    Returns a file-like object

    """
    url_split = urlparse.urlsplit(location)
    #pylint: disable-msg=E1103
    if url_split.scheme == "ftp":
        #pylint: disable-msg=E1103
        server = url_split.netloc
        user, password, root = get_ftp_password(server)
        ftp = ftplib.FTP(server, user, password)
        if root:
            ftp.cwd(root)
        class Transfer:
            pass
        Transfer.data = ""
        #pylint: disable-msg=E1103
        cmd = "RETR " + url_split.path
        def retr_callback(data):
            Transfer.data += data
        ftp.retrbinary(cmd, retr_callback)
        return StringIO.StringIO(Transfer.data)
    else:
        return urllib2.urlopen(location)



def download(url, output_dir,
    output_name=None,
    callback=callback,
    clobber=True,
    message=None):
    """ Download a file from an url, and save it
    in output_dir.

    The name of the file will be the basename of the url, unless
    output_name is given
    and a nice progressbar will be printed during the download

    If clobber is False, the file won't be overwritten if it
    already exists

    Returns the path to the downloaded file

    """
    qibuild.sh.mkdir(output_dir, recursive=True)
    if output_name:
        dest_name = os.path.join(output_dir, output_name)
    else:
        dest_name = url.split("/")[-1]
        dest_name = os.path.join(output_dir, dest_name)

    error = None

    if os.path.exists(dest_name) and not clobber:
        return dest_name

    if message:
        LOGGER.info(message)

    try:
        dest_file = open(dest_name, "wb")
    except Exception, e:
        mess  = "Could not save %s to %s\n" % (url, dest_name)
        mess += "Error was %s" % e
        raise Exception(mess)

    url_split = urlparse.urlsplit(url)
    url_obj = None
    try:
        #pylint: disable-msg=E1103
        if url_split.scheme == "ftp":
        # We cannot use urllib2 here because it has no support
        # for username/password for ftp, so we will use ftplib
        # here.
            #pylint: disable-msg=E1103
            server = url_split.netloc
            user, password, root = get_ftp_password(server)
            ftp = ftplib.FTP(server, user, password)
            if root:
                ftp.cwd(root)
            class Tranfert:
                pass
            #pylint: disable-msg=E1103
            size = ftp.size(url_split.path)
            Tranfert.xferd = 0
            def retr_callback(data):
                Tranfert.xferd += len(data)
                if callback:
                    callback(size, Tranfert.xferd)
                dest_file.write(data)
            #pylint: disable-msg=E1103
            cmd = "RETR " + url_split.path
            ftp.retrbinary(cmd, retr_callback)
        else:
            url_obj = urllib2.urlopen(url)
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
    except Exception, e:
        error  = "Could not dowload file from %s\n to %s\n" % (url, dest_name)
        error += "Error was: %s" % e
    finally:
        dest_file.close()
        if url_obj:
            url_obj.close()
    if error:
        qibuild.sh.rm(dest_name)
        raise Exception(error)

    return dest_name


