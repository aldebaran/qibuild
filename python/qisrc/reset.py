#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" A set of functions to help resetting repositories """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import qisrc.git
from qisys import ui


def _switch_to_git_ref(git, ref_to_reset_to, is_tag):
    """ Switch To Git Ref """
    if is_tag:
        # checkout puts the git current repo in a detached HEAD status
        # As setting a tag in the manifest means oubvioulsy a read-only git copy,
        # The detached HEAD prevents an user to accidentally pull up to the original branch HEAD and commits things
        rc, out = git.checkout(ref_to_reset_to, "--", raises=False)
    else:
        # reset --hard keeps the attached HEAD, and that's probably what the user needs to be able to track changes
        # and commits some things. If the user wants its git copy in read-only, he can use a tag instead of a branch
        rc, out = git.reset("--hard", ref_to_reset_to, "--", raises=False)
    return rc, out


def _reset_hard_to_refs_prefixed_ref(git, remote_name, ref, raises=True):
    """ deals with the git reset --hard command for long name ref (on the format 'refs/xxx') """
    assert ref.startswith("refs/")
    # Check the ref format to retrieve the effective ref name to switch on
    if ref.startswith("refs/remotes") and "/{}/".format(remote_name) in ref:
        # When the ref format begin with refs/remotes/<remote_name>/, that's the format seen by the local (git show-ref)
        git.fetch(remote_name)
        ref_to_reset_to = ref
        is_tag = False
    else:
        # The ref is in the format seen by a remote (git ls-remote):
        # refs/heads/xxx, refs/tags/xxx, refs/remotes/<other_remote>/xxx, refs/merge-requests/xxx
        git.fetch(remote_name, ref)  # This command will write the pointed commit number into the pseudo ref FETCH_HEAD
        ref_to_reset_to = "FETCH_HEAD"
        is_tag = ref.startswith("refs/tags")
    # Perform effective switch
    rc, out = _switch_to_git_ref(git, ref_to_reset_to, is_tag)
    return None if raises else (rc == 0), out


def _reset_hard_to_local_refs_name(git, remote_name, ref, raises=True):
    """ deals with the git reset --hard command for short name ref (NOT on the format 'refs/xxx') """
    need_to_fetch, _ = git.call("show", "--oneline", ref, "--", raises=False)
    if need_to_fetch:
        git.fetch(remote_name, "--tags")
    # else: SHA-1 already exists locally, no need to fetch
    _, tag_list = git.tag("-l", ref, raises=False)
    is_tag = ref == tag_list
    # Perform effective switch
    rc, out = _switch_to_git_ref(git, ref, is_tag)
    return None if raises else (rc == 0), out


def clever_reset_ref(git_project, ref, raises=True):
    """ Resets only if needed, fetches only if needed """
    try:
        remote_name = git_project.default_remote.name
    except AttributeError:
        error_msg = "Project {} has no default remote, defaulting to origin"
        ui.error(error_msg.format(git_project.name))
        remote_name = "origin"
    git = qisrc.git.Git(git_project.path)
    # Deals with "refs/" prefixed ref first
    if ref.startswith("refs/"):
        return _reset_hard_to_refs_prefixed_ref(git, remote_name, ref, raises=raises)
    # Else, ref format is a local name (branch or tag)
    # Check if this ref exists and if we are already in the expected state
    rc, ref_sha1 = git.call("rev-parse", ref, "--", raises=False)
    if rc != 0:
        # Maybe this is a newly pushed tag, try to fetch:
        git.fetch(remote_name)
        rc, ref_sha1 = git.call("rev-parse", ref, "--", raises=False)
        if rc != 0:
            return False, "Could not parse %s as a valid ref" % ref
    _, actual_sha1 = git.call("rev-parse", "HEAD", raises=False)
    if actual_sha1 == ref_sha1:  # Nothing to do
        return None if raises else True, ""
    # Reset to the ref local name
    return _reset_hard_to_local_refs_name(git, remote_name, ref, raises=raises)
