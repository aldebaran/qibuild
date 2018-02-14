# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Handling pushing changes to gerrit

"""

import os
import sys
import subprocess

import qisrc.git
from qisys import ui
import qisys.interact
import qisys.command
import qibuild.config


def fetch_gerrit_hook_ssh(path, username, server, port=None):
    """ Fetch the ``commit-msg`` hook from gerrit

    """
    if port is None:
        port = 22
    git_hooks_dir = os.path.join(path, ".git", "hooks")
    # Create the dir if doesn't exist (otherwise scp won't create it)
    if not os.path.isdir(git_hooks_dir):
        qisys.sh.mkdir(git_hooks_dir)
    if sys.platform.startswith("win"):
        # scp on git bash does not handle DOS paths:
        git_hooks_dir = qisys.sh.to_posix_path(git_hooks_dir, fix_drive=True)
    scp = qisys.command.find_program("scp", raises=False)
    if not scp:
        return False, "Could not find scp executable"
    cmd = [scp, "-P", str(port),
           "%s@%s:hooks/commit-msg" % (username, server),
           git_hooks_dir]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    (out, _) = process.communicate()
    if process.returncode == 0:
        return True, ""

    return False, out


def check_gerrit_connection(username, server, ssh_port=29418):
    """ Check that the user can connect to gerrit with ssh """
    cmd = ["ssh", "-p", str(ssh_port)]
    if os.environ.get("DISABLE_SSH_CHECKING"):
        ui.warning("Use ssh with StrictHostKeyChecking=no")
        cmd.extend(["-o", "StrictHostKeyChecking=no"])
    cmd.extend(["{}@{}".format(username, server),
                "gerrit", "version"])
    try:
        qisys.command.call(cmd, quiet=True)
    except qisys.command.CommandFailedException:
        return False
    return True


def ask_gerrit_username(server, ssh_port=29418):
    """ Run a wizard to try to configure gerrit access

    If that fails, ask the user for its username
    If that fails, give up and suggest upload the public key

    """
    ui.info(ui.green, "Configuring gerrit ssh access ...")
    username = os.environ.get("GERRIT_USER", qisys.sh.username())
    if not username:
        username = qisys.interact.ask_string("Please enter your username")
        if not username:
            return
    ui.info("Checking gerrit connection with %s@%s:%i" %
            (username, server, ssh_port))
    if check_gerrit_connection(username, server, ssh_port=ssh_port):
        ui.info("Success")
        return username

    ui.warning("Could not connect to ssh using username", username)
    try_other = qisys.interact.ask_yes_no("Do you want to try with another username?")
    if not try_other:
        return

    username = qisys.interact.ask_string("Please enter your username")
    if not username:
        return

    if check_gerrit_connection(username, server, ssh_port=ssh_port):
        return username


def get_gerrit_username(server, ssh_port):
    """ Get the username to use when using code review.

    Read it from the config file, or ask it and check it works
    """
    # Get username
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    access = qibuild_cfg.get_server_access(server)
    if access:
        username = access.username
    else:
        username = ask_gerrit_username(server, ssh_port=ssh_port)
        if not username:
            return None

    # Add it to config so we ask only once
    qibuild_cfg.set_server_access(server, username)
    qibuild_cfg.write()
    return username


def setup_project(project):
    """ Setup a project for code review:

    If there is :py:class:`.Remote` configured for code review,
    using the ssh protocol, use it to fetch the gerrit ``commit-msg`` hook

    """
    remote = project.review_remote
    server = remote.server
    username = remote.username
    ssh_port = remote.port

    # Install the hook
    commit_hook = os.path.join(project.path, ".git", "hooks", "commit-msg")
    if os.path.exists(commit_hook):
        return True
    ui.info("Configuring", ui.blue, project.src,
            ui.reset, "for code review ... ", end="")
    if remote.protocol == "ssh":
        ok, out = fetch_gerrit_hook_ssh(project.path, username, server, port=ssh_port)
        if not ok:
            ui.info("\n", out, ui.red, "[FAILED]")
            return False
    # FIXME: make it work with http too?
    ui.info(ui.green, "[OK]")
    return True


def push(project, branch, bypass_review=False, dry_run=False, reviewers=None, topic=None):
    # pylint: disable=too-many-locals
    """ Push the changes for review.

    Unless review is False, in this case, simply update
    the remote gerrit branch

    :param reviewers: A list of reviewers to invite to review

    """
    git = qisrc.git.Git(project.path)
    review_remote = project.review_remote
    args = list()
    if dry_run:
        args.append("--dry-run")
    args.append(review_remote.url)
    if bypass_review:
        args.append("%s:%s" % (branch, branch))
    else:
        ui.info("Pushing code to", review_remote.name, "for review.")
        remote_ref = "refs/for/%s" % branch
        if topic:
            remote_ref = "%s/%s" % (remote_ref, topic)
        args.append("%s:%s" % (branch, remote_ref))
    if reviewers and not dry_run:
        # Get the SHA1s that will be pushed so that we can add reviewers
        remote = project.review_remote
        remote.parse_url()
        server = remote.server
        username = remote.username
        ssh_port = remote.port
        ui.info("Fetching", remote.name)
        git.fetch(remote.name, "--quiet")
        commits_pushed = git.get_log("%s/%s" % (remote.name, branch), "HEAD")
        sha1s = [commit["sha1"] for commit in commits_pushed]
    git.push(*args)
    if reviewers and not dry_run:
        ui.info("Adding reviewers...", ("(" + ", ".join(reviewers) + ")"))
        try:
            set_reviewers(sha1s, reviewers, username, server, ssh_port)
        except qisys.command.CommandFailedException as e:
            ui.warning("Couldn't set reviewers")
            ui.warning(e)
        else:
            ui.info("Done!")


def set_reviewers(refs, reviewers, username, server, ssh_port):
    """ Set reviewers using gerrit set-reviewers command

    :param refs: A list of references to ``patchsets``, can be SHA1s or Change-Ids
    :param reviewers: A list of Gerrit reviewers, username or group name,
                      no e-mails
    """
    cmd = ["ssh", "-p", str(ssh_port),
           "%s@%s" % (username, server),
           "gerrit", "set-reviewers"]
    cmd.extend(refs)
    for reviewer in reviewers:
        cmd.append("--add %s" % reviewer)
    qisys.command.call(cmd, quiet=True)
