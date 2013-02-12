## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with a manifest

"""

import os
import operator

import qisys.sh
import qisrc.manifest
import qisrc.review
import qisrc.git
from qisys import ui

from qisrc.sync_build_profiles import sync_build_profiles

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
    manifest = worktree.get_project(src)
    if not manifest:
        clone_project(worktree, manifest_git_url, src=src)
        manifest = worktree.get_project(src)
    # Make sure manifest project is on the correct, up to date branch:
    git = qisrc.git.Git(manifest.path)
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

def fetch_load_manifest(worktree, manifest_git_url, branch="master",
    profile="default",
    src="manifest/default"):
    """ Fetch the manifest and load it.
    Return a Manifest with the fetched manifest
    """
    manifest_file = fetch_manifest(worktree, manifest_git_url, branch, profile, src)
    return qisrc.manifest.load(manifest_file)


def init_worktree(worktree, manifest, setup_review=True):
    """ (re)-initialize a worktree given a manifest.
    Clonie any missing repository, set the correct
    remote and tracking branch on every repository

    :param setup_review: Also set up the projects for review
    """
    errors = list()
    if not manifest.projects:
        return
    project_count = len(manifest.projects)
    ui.info(ui.green, "Initializing worktree ...")
    setup_ok = True
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
        wt_project = worktree.get_project(p_src)
        if not wt_project:
            # Maybe we just need to add the project to the worktree:
            wt_project = add_if_missing(worktree, p_src, p_remote, p_url)
            if not wt_project:
                wt_project = clone_project(worktree, p_url, src=p_src,
                                           branch=p_revision,
                                           remote=p_remote)
        p_path = wt_project.path
        if project.review and setup_review and setup_ok:
            worktree.set_project_review(p_src)
            # If setup failed once, no point in trying for every project
            setup_ok = qisrc.review.setup_project(p_path, project.name,
                                                  project.review_url)
        git = qisrc.git.Git(p_path)
        git.set_remote(p_remote, p_url)
        git.set_tracking_branch(p_revision, p_remote)
        cur_branch = git.get_current_branch()
        if cur_branch != p_revision:
            if not cur_branch:
                ui.warning("Project", project.name, "is on a detached HEAD",
                    "but should be on", p_revision)
            else:
                ui.warning("Project", project.name, "is on", cur_branch,
                    "but should be on", p_revision)
        worktree.set_git_project_config(p_src, p_remote, p_revision)
    if not setup_ok:
        qisrc.review.warn_gerrit()


def clone_project(worktree, url, src=None, branch=None, remote="origin"):
    """ Add a project to a worktree given its url.

    If src is not given, it will be guessed from the url

    """
    should_add = True
    if not src:
        src = url.split("/")[-1].replace(".git", "")
    if os.path.isabs(src):
        src = os.path.relpath(src, worktree.root)
        src = qisys.sh.to_posix_path(src)
    else:
        src = qisys.sh.to_posix_path(src)

    conflict_project = worktree.get_project(src, raises=False)
    if conflict_project:
        mess  = "Could not add project from %s in %s\n" % (url, src)
        mess += "This path is already registered for worktree in %s\n" % \
                worktree.root
        raise Exception(mess)

    path = os.path.join(worktree.root, src)
    path = qisys.sh.to_native_path(path)
    if os.path.exists(path):
        mess  = "Could not add project from %s in %s\n" % (url, src)
        mess += "This path already exists\n"
        raise Exception(mess)

    ui.info(ui.green, "Git clone: %s -> %s" % (url, path))
    dirname = os.path.dirname(path)
    qisys.sh.mkdir(dirname, recursive=True)
    git = qisrc.git.Git(path)
    if branch:
        git.clone(url, "-b", branch, "-o", remote)
    else:
        git.clone(url, "-o", remote)
    git.update_submodules()
    if should_add:
        worktree.add_project(path)
    return worktree.get_project(src)

def add_if_missing(worktree, src, remote_name, remote_url):
    """ Add a project to a worktree if src is a already a git repo with
    the correct remote url

    (can happen when someone runs qisrc remove then qisrc sync ...)
    """
    path = os.path.join(worktree.root, src)
    if not os.path.exists(path):
        return
    git_dir = os.path.join(path, ".git")
    if not os.path.exists(git_dir):
        raise Exception("%s already exists and is not a git repository" % path)
    if qisrc.git.is_submodule(path):
        repo_root = qisrc.git.get_repo_root(os.path.dirname(path))
        raise Exception("%s is already a submodule of %s" % (path, repo_root))
    git = qisrc.git.Git(path)
    git.set_remote(remote_name, remote_url)
    worktree.add_project(src)
    return worktree.get_project(src)

def sync_all(worktree, args):
    """ Fetch any manifest project, re init everything,
    re-create branch configurations, review setup and so on

    """
    manifest_projects = worktree.get_manifest_projects()
    if not manifest_projects:
        raise qisrc.manifest.NoManifest(worktree)
    # Re-synchronize everything:
    for manifest_project in manifest_projects:
        ui.info(ui.green, "Updating", manifest_project.src, "...")
        git = qisrc.git.Git(manifest_project.path)
        git.pull(quiet=True)
        manifest_filename = manifest_project.profile + ".xml"
        manifest_xml = os.path.join(manifest_project.path, manifest_filename)
        manifest = qisrc.manifest.load(manifest_xml)
        qisrc.sync.init_worktree(worktree, manifest, setup_review=args.setup_review)
        sync_build_profiles(worktree, manifest_xml)

def get_toplevel_git_projects(projects):
    """Return a sorted list of git_projects without submodules and without
    manifests.
    """
    git_projects = (x.git_project for x in projects if x.git_project and not x.manifest)

    git_projects = list(set(git_projects))

    git_projects.sort(key = operator.attrgetter("src"))

    return git_projects

