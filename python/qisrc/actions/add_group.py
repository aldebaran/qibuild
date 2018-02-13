# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
""" Add a group to the current worktree

"""
import copy
import sys

from qisys import ui
import qisrc.parsers


def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("group")


def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    group = args.group
    manifest = git_worktree.manifest
    if git_worktree.manifest.groups is None:
        groups = list()
    else:
        groups = copy.copy(git_worktree.manifest.groups)
    if group in groups:
        ui.error("Group", group, "already in use")
        sys.exit(1)
    else:
        groups.append(args.group)
    git_worktree.configure_manifest(manifest.url, groups=groups,
                                    branch=manifest.branch)
