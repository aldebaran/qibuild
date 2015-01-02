## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" A set of functions to help resetting repositories """

from qisys import ui
import qisrc.git


def clever_reset_ref(git_project, ref):
    """ Resets only if needed, fetches only if needed """
    try:
        remote_name = git_project.default_remote.name
    except AttributeError:
        error_msg = "Project {} has no default remote, defaulting to origin"
        ui.error(error_msg.format(git_project.name))
        remote_name = "origin"

    git = qisrc.git.Git(git_project.path)
    if ref.startswith("refs/"):
        git.fetch(remote_name, ref)
        git.reset("--hard", "FETCH_HEAD")
        return
    _, actual_sha1 = git.call("rev-parse", "HEAD", raises=False)
    if actual_sha1 == ref:  # Nothing to do
        return
    ret, _ = git.call("show", "--oneline", ref, raises=False)
    if ret == 0:  # SHA-1 exists locally
        git.reset("--hard", ref)
    else:  # Full fetch in this case
        git.fetch(remote_name)
        git.reset("--hard", ref)

