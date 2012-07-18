## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with a manifest

"""

import os
import sys

import qibuild.sh
import qisrc.manifest
import qisrc.review
import qisrc.git
from qibuild import ui


def fetch_manifest(worktree, manifest_git_url, branch="master",
    profile="default",
    src="manifest/default"):
    """ Fetch the manifest for a worktree

    :param manifest_git_url: A git repository containing a
        'manifest.xml' file, ala repo
    :param branch: The branch to use
    :param src: The path where to store the clone of the manifest

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
    filename = profile + ".xml"
    manifest_file = os.path.join(manifest.path, filename)
    if not os.path.exists(manifest_file):
        mess  = "Could not find a file named '%s' " % filename
        mess += "in the repository: %s\n" % manifest_git_url
        raise Exception(mess)
    return manifest_file


def init_worktree(worktree, manifest_location, setup_review=True):
    """ (re)-intianlize a worktree given a manifest location.
    Clonie any missing repository, set the correct
    remote and tracking branch on every repository

    :param setup_review: Also set up the projects for review
    """
    errors = list()
    manifest = qisrc.manifest.load(manifest_location)
    if not manifest.projects:
        return
    project_count = len(manifest.projects)
    ui.info(ui.green, "Initializing worktree ...")
    for i, project in enumerate(manifest.projects):
        ui.info(
            ui.green, "*", ui.reset, "(%2i/%2i)" % (i+1, project_count),
            ui.blue, project.name)
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
        wt_project = worktree.get_project(p_src)
        p_path = wt_project.path
        if project.review and setup_review:
            worktree.set_project_review(p_src, True)
            qisrc.review.setup_project(p_path, project.name, project.review_url, p_revision)
        git = qisrc.git.Git(p_path)
        git.set_remote(p_remote, p_url)
        git.set_tracking_branch(p_revision, p_remote)
        cur_branch = git.get_current_branch()
        if cur_branch != p_revision:
            ui.warning("Project", project.name, "is on", cur_branch,
                "should be in", p_revision)
        worktree.set_git_project_config(p_src, p_remote, p_revision)


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
                ui.debug("Found project in %s, skipping" % src)
                return
            # Some one erase the project manually without telling qiworktree
            should_add = False

    path = os.path.join(worktree.root, src)
    path = qibuild.sh.to_native_path(path)
    if os.path.exists(path):
        if skip_if_exists:
            if qisrc.git.is_submodule(path):
                ui.warning("erasing submodule: ", path)
                qibuild.sh.rm(path)
            else:
                ui.debug("Adding project in %s", src)
                worktree.add_project(src)
                return
        else:
            mess  = "Could not add project from %s in %s\n" % (url, src)
            mess += "This path already exists\n"
            raise Exception(mess)

    ui.info(ui.green, "Git clone: %s -> %s" % (url, path))
    dirname = os.path.dirname(path)
    qibuild.sh.mkdir(dirname, recursive=True)
    git = qisrc.git.Git(path)
    if branch:
        git.clone(url, "-b", branch, "-o", remote)
    else:
        git.clone(url, "-o", remote)
    if should_add:
        worktree.add_project(path)
