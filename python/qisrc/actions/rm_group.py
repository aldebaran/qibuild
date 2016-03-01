## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
""" Remove a group from the current worktree

"""

from qisys import ui
import qisys.interact
import qisys.sh
import qisrc.parsers

import sys
import copy

def configure_parser(parser):
    qisrc.parsers.worktree_parser(parser)
    parser.add_argument("group")
    parser.add_argument("--from-disk", dest="from_disk", action="store_true",
        help="Also remove project sources from disk")
    parser.set_defaults(from_disk=False)

def remove_from_disk(projects):
    ui.warning("Would remove the following projects from disk:")
    for i, project in enumerate(projects):
        ui.info_count(i, len(projects), project.src)
    ui.warning("This cannot be undone!",
               "Make sure there are not any local modifications you care about",
               "in the projects you are going to remove", sep="\n")
    proceed = qisys.interact.ask_yes_no("Proceed?", default=False)
    if proceed:
        ui.info(ui.green, "Removing projects:")
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects), project.src)
            qisys.sh.rm(project.path)

def do(args):
    git_worktree = qisrc.parsers.get_git_worktree(args)
    group = args.group
    manifest = git_worktree.manifest
    groups = copy.copy(git_worktree.manifest.groups)
    old_groups = groups
    if group in groups:
        new_groups = copy.copy(groups)
        new_groups.remove(group)
    else:
        ui.info("No such group:", group)
        sys.exit(0)

    # If we have called `qisrc sync` after a group is removed from the manifest,
    # the .qi/manifests/default/manifest.xml file will no longer contain
    # the group we are trying to remove, so ignore errors due to missing
    # groups for this call.
    # This is because git_worktree.get_git_projects()
    # will call qisrc.groups.get_groups(worktree), which will re-read groups
    # from .qi/manifests/default/manifest.xml, instead of
    # using groups from the local manifest in .qi/manifests.xml
    # (which are names, and not qisrc.group.Group instances anyway)
    old_projects = set(git_worktree.get_git_projects(groups=old_groups,
                                                     ignore_missing_groups=True))
    git_worktree.configure_manifest(manifest.url, groups=new_groups,
                                    branch=manifest.branch)

    new_projects = set(git_worktree.get_git_projects(groups=new_groups))
    to_remove = sorted(old_projects - new_projects)

    if args.from_disk:
        remove_from_disk(to_remove)
