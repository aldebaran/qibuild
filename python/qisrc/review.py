## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling pushing changes to gerrit

"""

import os
import re
import urlparse

import qisrc.git
import qibuild.interact


def parse_git_url(url):
    """ Parse a git url. Return a tuple: username, server, port

    """
    match = re.match("(ssh://)?(?P<username>\w+)@(?P<server>\w+)(:(?P<port>\d+))?",
        url)
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
    netloc = urlparse.urlsplit(url).netloc
    server = netloc.split(":")[0]
    res = "ssh://%s@%s:%i/%s" % (username, server, gerrit_ssh_port, project_name)
    return res



def fetch_gerrit_hook(username, server, port, path):
    """ Fetch the commint-msg hook from gerrit

    """
    git_hooks_dir = os.path.join(path, ".git", "hooks")
    cmd = ["scp", "-p", str(port),
        "%s@%s" % (username, server),
        git_hooks_dir]
    qibuild.command.call(cmd)


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

def ask_username():
    """ Just a helper for guess_user_name

    """
    res = qibuild.interact.ask_string("Please enter your username ")
    if res:
        return res
    return

def guess_user_name(server, gerrit_ssh_port=29418):
    """" Guess the username to use by trying to
    log in to the server with the current user name

    If that fails, ask the user for its username
    If that fails, give up and suggest upload the public key

    """
    # works on UNIX and git bash:
    username = os.environ.get("USERNAME")
    if not username:
        username = ask_username()
        if not username:
            return

    if check_gerrit_connection(username, server, gerrit_ssh_port):
        return username

    print "Could not connect to ssh using username", username
    try_other = qibuild.interact.ask_yes_no("Do you want to try with an other username ?")
    if not try_other:
        return

    username = ask_username()
    if not username:
        return

    if check_gerrit_connection(username, server, gerrit_ssh_port):
        return username


def setup_project(project_path, project_name, review_url, branch):
    """ Setup a project for code review.
     - Figure out the user name
     - Add a remote called 'gerrit'
     - Add the hook
    """
    git = qisrc.git.Git(project_path)
    remote_url = git.get_config("remote.gerrit.url")
    if not remote_url:
        # Extract server from url:
        netloc = urlparse.urlsplit(review_url).netloc
        server = netloc.split(":")[0]

        username = guess_user_name(server)
        if not username:
            print "qisrc: could not find your gerrit username"
            print "You will not be able to submit for code review"
            return
        remote_url = http_to_ssh(review_url, project_name, username)
        git.set_remote("gerrit", remote_url)


def setup_hook(project_path, remote_url):
    """ Add the commit-msg hook to a project

    """
    (username, server, port) = parse_git_url(remote_url)
    commit_hook = os.path.join(project_path, ".git", "hooks", "commit-msg")
    if os.path.exists(commit_hook):
        return
    fetch_gerrit_hook(project_path, username, server, port)



def update(project_path, branch, review=True):
    """ Push the changes for review.
    Unless review is False, in this case, simply update
    the remote gerrit branch

    """
    git = qisrc.git.Git(project_path)
    if review:
        git.push("gerrit", "%s:refs/for/%s" % (branch, branch))
    else:
        git.push("gerrit", "%s:%s" % (branch, branch))
