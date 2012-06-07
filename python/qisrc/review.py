## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling pushing changes to gerrit

"""

import os
import re
import sys
import logging
import urlparse

import qisrc.git
import qibuild.interact
import qibuild.config

LOGGER = logging.getLogger(__name__)

def parse_git_url(url):
    """ Parse a git url. Return a tuple: username, server, port

    """
    match = re.match(r"""
        (ssh://)?
        (?P<username>[a-zA-Z0-9\._-]+)
        @
        (?P<server>[a-zA-Z0-9\._-]+)
        (:(?P<port>\d+))?
    """, url, re.VERBOSE)
    if not match:
        return None
    groupdict = match.groupdict()
    username = groupdict["username"]
    server = groupdict["server"]
    port = groupdict["port"]
    return (username, server, port)


def http_to_ssh(url, project_name, username, gerrit_ssh_port=29418):
    """ Return an ssh url from a http gerrit url and a username

    """
    # Extract server from url:
    # pylint: disable-msg=E1103
    netloc = urlparse.urlsplit(url).netloc
    server = netloc.split(":")[0]
    res = "ssh://%s@%s:%i/%s" % (username, server, gerrit_ssh_port, project_name)
    return res



def fetch_gerrit_hook(path, username, server, port):
    """ Fetch the ``commit-msg`` hook from gerrit

    """
    git_hooks_dir = os.path.join(path, ".git", "hooks")
    if sys.platform.startswith("win"):
        # scp on git bash does not handle DOS paths:
        git_hooks_dir = qibuild.sh.to_posix_path(git_hooks_dir, fix_drive=True)
    cmd = ["scp", "-P" , str(port),
        "%s@%s:hooks/commit-msg" % (username, server),
        git_hooks_dir]
    qibuild.command.call(cmd, quiet=True)


def check_gerrit_connection(username, server, gerrit_ssh_port=29418):
    """ Check that the user can connect to gerrit with ssh """
    cmd = ["ssh", "-p", str(gerrit_ssh_port),
        "%s@%s" % (username, server),
        "gerrit", "version"]
    try:
        qibuild.command.call(cmd, quiet=True)
    except qibuild.command.CommandFailedException:
        return False
    return True

def ask_gerrit_username(server, gerrit_ssh_port=29418):
    """ Run a wizard to try to configure gerrit access

    If that fails, ask the user for its username
    If that fails, give up and suggest upload the public key

    """
    LOGGER.info("Configuring gerrit ssh access ...")
    # works on UNIX and git bash:
    username = os.environ.get("USERNAME")
    if not username:
        username = qibuild.interact.ask_string("Please enter your username")
        if not username:
            return
    LOGGER.info("Checking gerrit connection with %s@%s:%i",
        username, server, gerrit_ssh_port)
    if check_gerrit_connection(username, server, gerrit_ssh_port):
        LOGGER.info("Success")
        return username

    print "Could not connect to ssh using username", username
    try_other = qibuild.interact.ask_yes_no("Do you want to try with an other username ?")
    if not try_other:
        return

    username = qibuild.interact.ask_string("Please enter your username ")
    if not username:
        return

    if check_gerrit_connection(username, server, gerrit_ssh_port):
        return username


def setup_project(project_path, project_name, review_url, branch):
    """ Setup a project for code review.

     * Figure out the user name
     * Add a remote called 'gerrit'
     * Add the hook

    """
    git = qisrc.git.Git(project_path)
    # Extract server from url:
    # pylint: disable-msg=E1103
    netloc = urlparse.urlsplit(review_url).netloc
    server = netloc.split(":")[0]

    # Get username
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    access = qibuild_cfg.get_server_access(server)
    if access:
        username = access.username
    else:
        username = ask_gerrit_username(server)
        if not username:
            return

    # Add it to config so we ask only once
    qibuild_cfg.set_server_access(server, username)
    qibuild_cfg.write()

    # Set a remote named 'gerrit'
    remote_url = http_to_ssh(review_url, project_name, username)
    git.set_remote("gerrit", remote_url)

    # Install the hook
    commit_hook = os.path.join(project_path, ".git", "hooks", "commit-msg")
    if os.path.exists(commit_hook):
        return
    (username, server, port) = parse_git_url(remote_url)
    fetch_gerrit_hook(project_path, username, server, port)



def push(project_path, branch, review=True, dry_run=False):
    """ Push the changes for review.
    Unless review is False, in this case, simply update
    the remote gerrit branch

    """
    git = qisrc.git.Git(project_path)
    args = ["gerrit"]
    if dry_run:
        args.append("--dry-run")
    if review:
        args.append("%s:refs/for/%s" % (branch, branch))
    else:
        args.append("%s:%s" % (branch, branch))
    git.push(*args)
