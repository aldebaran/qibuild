## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" A set of functions to help resetting repositories """

from qisys import ui
import qisrc.git


def clever_reset_ref(git_project, ref, raises=True):
    """ Resets only if needed, fetches only if needed """
    try:
        remote_name = git_project.default_remote.name
    except AttributeError:
        error_msg = "Project {} has no default remote, defaulting to origin"
        ui.error(error_msg.format(git_project.name))
        remote_name = "origin"

    git = qisrc.git.Git(git_project.path)
    if ref.startswith("refs/"):
        if raises:
            git.fetch(remote_name, ref)
            git.reset("--hard", "FETCH_HEAD")
            return
        else:
            with git.tansaction() as transaction:
                git.fetch(remote_name, ref)
                git.reset("--hard", "FETCH_HEAD")
                return transaction.ok, transaction.output

    rc, ref_sha1 = git.call("rev-parse", ref, raises=False)
    if rc != 0:
        # Maybe this is a newly pushed tag, try to fetch:
        git.fetch(remote_name)
        rc, ref_sha1 = git.call("rev-parse", ref, raises=False)
        if rc != 0:
            return False, "Could not parse %s as a valid ref" % ref
    _, actual_sha1 = git.call("rev-parse", "HEAD", raises=False)
    if actual_sha1 == ref_sha1:  # Nothing to do
        if raises:
            return
        else:
            return True, ""
    ret, _ = git.call("show", "--oneline", ref, raises=False)
    if ret == 0:  # SHA-1 exists locally
        if raises:
            git.reset("--hard", ref)
        else:
            rc, out = git.reset("--hard", ref, raises=False)
            return (rc == 0), out
    else:  # Full fetch in this case
        if raises:
            git.fetch(remote_name)
            git.reset("--hard", ref)
        else:
            with git.transaction() as transaction:
                git.fetch(remote_name)
                git.reset("--hard", ref)
            return transaction.ok, transaction.output
