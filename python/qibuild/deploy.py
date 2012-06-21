## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Tools to deploy files to remote targets"""

import re
import os

import qibuild.command

def parse_url(remote_url):
    """ Parse a remote url

    :return: a tuple: (username, host, path)

    """
    match = re.match(r"""
        ((?P<username>[a-zA-Z0-9\._-]+)@)?
        (?P<server>[a-zA-Z0-9\._-]+)
        :
        (?P<path>[a-zA-A0-9\._/-]*)
        """, remote_url, re.VERBOSE)
    if not match:
        mess  = "Invalid remote url: %s\n" % remote_url
        mess += "Remote url should look like user@host:path"
        raise Exception(mess)
    groupdict = match.groupdict()
    username = groupdict["username"]
    if not username:
        username = os.environ.get("USERNAME")
    server = groupdict["server"]
    path = groupdict["path"]
    return (username, server, path)


def deploy(local_directory, remote_url, port=22, use_rsync=True):
    """ Deploy a local directory to a remote url

    """
    (username, server, path) = parse_url(remote_url)
    if use_rsync:
        # This is required for rsync to do the right thing,
        # otherwise the basename of local_directory gets
        # created
        local_directory = local_directory + "/."
        cmd = ["rsync",
            "--archive",  # presevre symlinks et all
            "--update",   # only copy newer files
            "--progress", # print a progress bar
            "--checksum", # verify checksum instead of size and date
            "-e", "ssh -p %d" % port, # custom ssh port
            local_directory, remote_url
        ]
        qibuild.command.call(cmd)
    else:
        # Default to scp
        qibuild.command.call(["scp", "-p", str(port), "-r",
            local_directory, remote_url])
