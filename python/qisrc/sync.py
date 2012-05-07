## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with a manifest

"""

import os
import sys
import logging

import qibuild.sh

import qisrc.manifest
import qisrc.review
import qisrc.git

LOGGER = logging.getLogger(__name__)

def indent(text, num):
    """ Indent a piece of text """
    lines = text.splitlines()
    lines = [" " * num + l for l in lines]
    return "\n".join(lines)

def fetch_manifest(worktree, manifest_git_url, branch="master", src="manifest/default"):
    """ Fetch the manifest for a worktree

    :param manifest_git_url: A git repository containing a
        'manifest.xml' file, ala repo
    :parm branch: The branch to use

    Note: every changes made by the user directly in the manifest repo
    will be lost!

    """
    clone_project(worktree, manifest_git_url, src=src, skip_if_exists=True)
    # Make sure manifest project is on the correct, up to date branch:
    manifest = worktree.get_project(src)
    git = qisrc.git.open(manifest.path)
    git.set_remote("origin", manifest_git_url)
    git.set_tracking_branch(branch, "origin")
    git.checkout("-f", branch, quiet=True)
    git.fetch(quiet=True)
    git.reset("--hard", "origin/%s" % branch, quiet=True)
    manifest_xml = os.path.join(manifest.path, "manifest.xml")
    return manifest_xml


def sync_projects(worktree, manifest_location, setup_review=True, update_branch=True):
    """ Synchronize a worktree with a manifest,
    cloning any missing repository, setting the correct
    remote and tracking branch on every repository

    :param setup_review: Also set up the project for review
    :param update_branch: Also update local branches when possible (fast-forward,
        pull --rebase without conflicts)

    """
    errors = list()
    manifest = qisrc.manifest.Manifest(manifest_location)
    if not manifest.projects:
        return
    project_count = len(manifest.projects)
    for i, project in enumerate(manifest.projects):
        print "Syncing project %i on %i (%s)" % (i+1, project_count, project.name)
        # Use the same branch for the project as the branch
        # for the manifest, unless explicitely set:
        p_revision = project.revision
        p_url = project.fetch_url
        p_remote = project.remote
        p_src = project.path
        clone_project(worktree, p_url,
                      src=p_src,
                      branch=p_revision,
                      remote=p_remote,
                      skip_if_exists=True)
        p_path = worktree.get_project(p_src).path
        if project.review and setup_review:
            qisrc.review.setup_project(p_path, project.name, project.review_url, p_revision)
        git = qisrc.git.Git(p_path)
        git.set_remote(p_remote, p_url)
        git.set_tracking_branch(p_revision, p_remote)
        if update_branch:
            error = git.update_branch(p_revision, p_remote, p_revision)
        else:
            error = None
        if error:
            errors.append((p_src, error))
    if not errors:
        return
    LOGGER.error("Fail to sync some projects")
    for (src, err) in errors:
        print src
        print "-" * len(src)
        print indent(err, 2)
        print


def pull_projects(worktree, rebase=False):
    """ Pull every project in a worktree

    """
    errors = list()
    projects = [p for p in worktree.git_projects if not p.manifest]
    pad = " " * max([len(p.src) for p in projects])
    project_count = len(projects)
    for i, project in enumerate(projects):
        sys.stdout.write("Pulling project %i on %i (%s)" %
            (i+1, project_count, project.src) + pad + "\r")
        sys.stdout.flush()
        git = qisrc.git.open(project.path)
        if rebase:
            (retcode, out) = git.pull("--rebase", raises=False)
        else:
            (retcode, out) = git.pull(raises=False)
        if retcode != 0:
            errors.append((project.src, out))
    if not errors:
        return
    LOGGER.error("Fail to pull some projects")
    for (src, err) in errors:
        print src
        print "-" * len(src)
        print
        print indent(err, 2)


def clone_project(worktree, url, src=None, branch=None, remote="origin",
    skip_if_exists=False):
    """ Add a project to a worktree given its url.

    If src is not given, it will be guessed from the url

    If skip_if_exists is False, an error message will be
    raised if the project already exists

    """
    should_add = True
    if not src:
        src = url.split("/")[-1].replace(".git", "")
    if os.path.isabs(src):
        src = os.path.relpath(worktree.root, src)
        src = qibuild.sh.to_posix_path(src)

    project = worktree.get_project(src, raises=False)
    if project:
        if not skip_if_exists:
            mess  = "Could not add project from %s in %s\n" % (url, src)
            mess += "This path is already registered for worktree in %s\n" % worktree.root
            raise Exception(mess)
        else:
            if os.path.exists(project.path):
                LOGGER.debug("Found project in %s, skipping" % src)
                return
            # Some one erase the project manually without telling qiworktree
            should_add = False

    path = os.path.join(worktree.root, src)
    if os.path.exists(path):
        if skip_if_exists:
            LOGGER.debug("Adding project in %s", src)
            worktree.add_project(src)
            return
        else:
            mess  = "Could not add project from %s in %s\n" % (url, src)
            mess += "This path already exists\n"
            raise Exception(mess)

    LOGGER.info("Git clone: %s -> %s", url, path)
    dirname = os.path.dirname(path)
    qibuild.sh.mkdir(dirname, recursive=True)
    git = qisrc.git.Git(path)
    if branch:
        git.clone(url, "-b", branch, "-o", remote)
    else:
        git.clone(url, "-o", remote)
    if should_add:
        worktree.add_project(path)
