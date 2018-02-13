# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

"""Reset repositories to a clean state

By default, make sure the repository is on the correct branch

"""

import sys

from qisys import ui
import qisys.parsers
import qisys.worktree
import qisys.interact
import qisrc.git
import qisrc.snapshot
import qisrc.status
import qisrc.parsers
import qisrc.reset


def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    parser.add_argument("-f", "--force", action="store_true",
                        help="Discard local changes")
    parser.add_argument("--tag", help="Reset everything to the given tag")
    parser.add_argument("--snapshot", help="Reset everything using the given "
                        "snapshot")
    parser.add_argument("--ignore-groups", dest="ignore_groups", action="store_true",
                        help="Ignore groups defined in the snapshot")
    parser.set_defaults(ignore_groups=False)


def do(args):  # pylint: disable=too-many-branches
    """Main entry points."""

    git_worktree = qisrc.parsers.get_git_worktree(args)
    snapshot = None
    if args.snapshot:
        snapshot = qisrc.snapshot.Snapshot()
        snapshot.load(args.snapshot)

    if snapshot and snapshot.format_version and snapshot.format_version >= 1:
        reset_manifest(git_worktree, snapshot,
                       ignore_groups=args.ignore_groups)

    git_projects = qisrc.parsers.get_git_projects(git_worktree, args,
                                                  default_all=True,
                                                  use_build_deps=True)
    errors = list()
    for i, git_project in enumerate(git_projects):
        ui.info_count(i, len(git_projects), "Reset", git_project.src)
        src = git_project.src
        git = qisrc.git.Git(git_project.path)
        ok, message = git.require_clean_worktree()
        if not ok and not args.force:
            ui.warning(message)
            errors.append(src)
            continue

        if not git_project.default_branch:
            if git_project.fixed_ref:
                qisrc.reset.clever_reset_ref(git_project, git_project.fixed_ref)
                continue

            ui.warning(git_project.src, "not in manifest, skipping")
            continue

        branch = git_project.default_branch.name
        remote = git_project.default_remote.name
        git.safe_checkout(branch, remote, force=True)

        to_reset = None
        if args.snapshot:
            to_reset = snapshot.refs.get(src)
            if not to_reset:
                ui.warning(src, "not found in the snapshot")
                continue
        elif args.tag:
            to_reset = args.tag
        else:
            to_reset = "%s/%s" % (remote, branch)
        try:
            qisrc.reset.clever_reset_ref(git_project, to_reset)
        except Exception:
            errors.append(src)

    if not errors:
        return
    ui.error("Failed to reset some projects")
    for error in errors:
        ui.info(ui.red, " * ", error)
    sys.exit(1)


def reset_manifest(git_worktree, snapshot, ignore_groups=False):
    manifest = snapshot.manifest
    if ignore_groups:
        groups = git_worktree.manifest.groups
    else:
        groups = manifest.groups
    if not manifest.branch:
        raise Exception("No branch configured for the manifest of the snapshot")
    ok = git_worktree.configure_manifest(manifest.url, groups=groups,
                                         branch=manifest.branch, ref=manifest.ref)
    if not ok:
        sys.exit(1)
