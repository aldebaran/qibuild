#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Copyright (c) 2012-2020 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license (see the COPYING file).
""" Computing diffs between manifest branches """
from __future__ import absolute_import
from __future__ import unicode_literals
from __future__ import print_function

import sys

import qisrc.git
import qisys.worktree
from qisys import ui


def diff_worktree(git_worktree, git_projects, branch, cmd=None):
    """ Run  `git <cmd> local_branch..remote_branch` for every project """
    if not cmd:
        cmd = ["log"]
    remote_projects = git_worktree.get_projects_on_branch(branch)
    for git_project in git_projects:
        remote_project = remote_projects.get(git_project.src)
        if not remote_project:
            continue
        git = qisrc.git.Git(git_project.path)
        local_branch = git.get_current_branch()
        if not local_branch:
            message = (ui.brown, "Not on a branch")
        else:
            remote_branch = remote_project.default_branch.name
            remote_ref = "%s/%s" % (remote_project.default_remote.name, remote_branch)
            rc, out = git.call("merge-base", local_branch, remote_ref, raises=False)
            if rc != 0:
                message = (ui.red, "Calling git merge-base failed")
            else:
                merge_base = out.strip()
                full_cmd = cmd + ["%s..%s" % (merge_base, local_branch)]
                color = ui.config_color(sys.stdout)
                if color:
                    full_cmd.append("--color=always")
                rc, out = git.call(*full_cmd, raises=False)
                if rc != 0:
                    message = (ui.red, "Calling git log failed")
                else:
                    if out:
                        message = (out,)
                    else:
                        continue
        ui.info(ui.bold, git_project.src)
        ui.info(ui.bold, "-" * len(git_project.src))
        ui.info(*message)
        ui.info()


def get_forked_projects(git_worktree, manifest_branch):
    """ Return a dict containing branches specified on a manifest

    - It can be either a default branch specified on top, affecting
      all projects in the worktree
    - Or a branch per project
    """
    if manifest_branch.startswith(("master", "release")):
        return list()
    git_projects = git_worktree.get_projects_on_branch(manifest_branch).values()
    forked_git_projects = list()
    for project in git_projects:
        for branch in project.branches:
            if branch.default and branch.name == manifest_branch:
                forked_git_projects.append(project)
    return forked_git_projects


def print_diff(git_project, manifest_branch, destination_branch):
    """
        Show what to merge in prepare_merge_request style
    """
    git = qisrc.git.Git(git_project.path)
    default_remote = git_project.default_remote
    if not default_remote:
        return True
    remote_name = default_remote.name
    if remote_name not in ["origin"]:
        return True
    default_branch = git_project.default_branch
    if not default_branch:
        return True
    if git_project.src == "manifest/default":
        return True
    git.fetch(remote_name, "--prune")
    devel_ref = "%s/%s" % (remote_name, manifest_branch)
    base_ref = "%s/%s" % (remote_name, destination_branch)
    status, message = qisrc.git.get_status(git, devel_ref, base_ref, with_message=True)
    pretty_name = git_project.name.split(".git")[0]
    ui.info(pretty_name, status, message)
    return status in ["no-diff", "ahead"]
