## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

from qisys import ui
import qisys.error
import qisys.interact

import qisrc.manifest

def rebase_worktree(git_worktree, git_projects, branch=None,
                    push=False, dry_run=False):
    if not git_projects:
        return
    upstream_projects = git_worktree.get_projects_on_branch(branch)
    to_push, errors = rebase_projects(git_projects, upstream_projects, branch)
    if errors:
        mess = "Failed to rebase some projects:\n"
        for git_project in errors:
            mess += " * " + git_project.src
            mess += "\n"
        raise qisys.error.Error(mess)

    if push:
        push_projects(to_push, dry_run=dry_run)

def push_projects(git_projects, dry_run=False):
    if not git_projects:
        ui.info(ui.green, "Nothing to push")
        return
    ui.info(ui.green, "Pushing", len(git_projects), "projects")
    for i, git_project in enumerate(git_projects):
        default_branch = git_project.default_branch.name
        remote_branch = git_project.default_branch.remote_branch
        ui.info_count(i, len(git_projects), git_project.src)
        git = qisrc.git.Git(git_project.path)
        if git_project.review:
            push_remote = git_project.review_remote
        else:
            push_remote = git_project.default_remote
        remote_ref = "%s/%s" % (push_remote.name, remote_branch)
        to_push = "%s:%s" % (default_branch, remote_branch)
        push_args = [push_remote.name, to_push]
        push_args.append("--force")
        if dry_run:
            push_args.append("--dry-run")
        rc, out = git.push(*push_args, raises=False)
        if rc == 0:
            ui.info(out)
        else:
            ui.error(out)

def rebase_projects(git_projects, upstream_projects, branch):
    """ Rebase all the forked project on top of the upstream
    branch

    Return a tuple (to_push, errors)

    """
    ui.info(ui.green, "Computing list of forked projects ...")
    forked_projects = get_forked_projects(git_projects, upstream_projects, branch)
    if not forked_projects:
        ui.info(ui.green, "Nothing to rebase")
        return list(), list()
    ui.info(ui.green, "Rebasing forked projects ...")
    errors = list()
    to_push = list()
    max_src = max(len(x.src) for x in forked_projects)
    for i, git_project in enumerate(forked_projects):
        ui.info_count(i, len(forked_projects),
                      git_project.src.ljust(max_src + 2), end="")
        upstream_project = upstream_projects[git_project.src]
        ok, rebased = rebase_project(git_project, upstream_project)
        if not ok:
            errors.append(git_project)
        if rebased:
            to_push.append(git_project)

    return to_push, errors

def get_forked_projects(git_projects, upstream_projects, branch):
    res = list()
    for git_project in git_projects:
        if not git_project.default_remote:
            continue
        if not git_project.default_branch:
            continue
        local_branch = git_project.default_branch.name
        remote_branch = git_project.default_branch.remote_branch
        remote_name = git_project.default_remote.name
        remote_ref = "%s/%s" % (remote_name, remote_branch)
        if not git_project.src in upstream_projects:
            ui.info(ui.brown, git_project.src, "[skipped]")
            ui.info("No match for %s on %s branch" % (git_project.src, branch))
            continue
        upstream_project = upstream_projects[git_project.src]
        upstream_branch = upstream_project.default_branch.name
        upstream_ref = "%s/%s" % (upstream_project.default_remote.name, upstream_branch)
        if remote_ref != upstream_ref:
            res.append(git_project)
    return res

def rebase_project(git_project, upstream_project):
    """ Rebase the development branch of the project on the
    base branch (from upstream_project)

    Returns a tuple (ok, should_push)

    * ok is True if rebase went well (either the repo was already up-to-date,
      or the rebase happened without conflicts)
    * should_push is True if the repo should be pushed (useful to avoid
      pushing already up-to-date repos)
    """
    ok = check_local_branch(git_project)
    if not ok:
        return False, False
    git = qisrc.git.Git(git_project.path)
    local_branch = git_project.default_branch.name
    upstream_branch = upstream_project.default_branch.name
    upstream_ref = "%s/%s" % (upstream_project.default_remote.name, upstream_branch)
    status = qisrc.git.get_status(git, local_branch, upstream_ref)
    if status == "ahead":
        ui.info(ui.green, "[OK]", ui.reset, "already rebased")
        return True, False
    if status == "no-diff":
        ui.info(ui.green, "[OK]", ui.reset, "no diff")
        return True, False
    if status == "behind":
        rc, out = git.merge(upstream_ref, raises=False)
        if rc != 0:
            ui.info(ui.red, "[FAILED]")
            ui.info(ui.red, "git merge failed\n" + out)
            return False, False
        ui.info(ui.green, "[OK]", ui.reset, "fast-forwarded")
        return True, True
    git.call("tag", "-f", "before-rebase", raises=False) # suppress output
    rc, out = git.call("rebase", upstream_ref, raises=False)
    if rc == 0:
        ui.info(ui.green, "[OK]", ui.reset, "rebased")
        return True, True
    else:
        ui.info(ui.red, "[FAILED]", ui.reset, "there was some conflicts")
        git.call("rebase", "--abort", raises=False)
        git.call("tag", "-d", "before-rebase", raises=False) # suppress output
        return False, False

def check_local_branch(git_project):
    git = qisrc.git.Git(git_project.path)
    rc, out = git.fetch(raises=False)
    if rc != 0:
        ui.info(ui.red, "[FAILED]")
        ui.info(ui.red, "git fetch failed:\n" + out)
        return False
    current_branch = git.get_current_branch()
    local_branch = git_project.default_branch.name
    if current_branch != local_branch:
        ui.info(ui.brown, "[skipped] ", end="")
        ui.info("On %s, should be on %s" % (current_branch, local_branch))
        return False
    return True
