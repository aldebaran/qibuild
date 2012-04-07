## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with a manifest

"""
import os
import sys
import logging

import qisrc.manifest
import qisrc.git

LOGGER = logging.getLogger(__name__)

def fetch_manifest(worktree, manifest_git_url):
    """ Fetch the manifest for a worktree

    The url should point to a git repository containing a
    'manifest.xml' file, ala repo

    """
    clone_project(worktree, manifest_git_url,
                  skip_if_exists=True)
    manifest = worktree.get_project("manifest")
    git = qisrc.git.open(manifest.src)
    git.pull(quiet=True)
    manifest_xml = os.path.join(manifest.src, "manifest.xml")
    return manifest_xml


def sync_worktree(worktree, rebase=True, manifest_location=None):
    """ Synchronize a worktree.
    :param manifest_locations: If given, must be a
        list of paths to xml files

    """
    if manifest_location is None:
        manifest_location = list()
    # First clone every missing repository using the manifest location
    manifest = qisrc.manifest.Manifest(manifest_location)
    for project in manifest.projects:
        if project.worktree_name:
            p_name = project.worktree_name
        else:
            # Here project.name is in fact the relative path
            # of the git url (for instance remote is git://foo.com,
            # and name is bar/bar.git), but we want 'bar'
            # as worktree project name:
            p_name = project.name.split("/")[-1].replace(".git", "")
        p_url = project.fetch_url
        p_path = project.path
        clone_project(worktree, p_url,
                      name=p_name,
                      path=p_path,
                      skip_if_exists=True)
    # Then pull everything
    pad = " " * max([len(p.name) for p in worktree.git_projects])
    project_count = len(worktree.git_projects)
    for i, git_project in enumerate(worktree.git_projects):
        sys.stdout.write("Pulling project %i on %i (%s)" %
            (i+1, project_count, git_project.name)
            + pad + "\r")
        sys.stdout.flush()
        git = qisrc.git.open(git_project.src)
        if rebase:
            git.pull("--rebase", quiet=True)
        else:
            git.pull(quiet=True)


def clone_project(worktree, url,
                  name=None,
                  path=None,
                  skip_if_exists=False):
    """ Add a project to a worktree given its url.

    If name is not given, it will be guessed from the
    url.
    If path is not given, it will be <worktree>/name
    If skip_if_exists is False, an error message will be
    raised if the project already exists

    """
    if not name:
        name = url.split("/")[-1].replace(".git", "")
    if not path:
        path = os.path.join(worktree.root, name)
    else:
        path = os.path.join(worktree.root, path)

    p_names = [p.name for p in worktree.projects]
    if name in p_names and not skip_if_exists:
        conflicting_project = worktree.get_project(name)
        mess  = "Could not add project %s from %s\n" % (name, url)
        mess += "A project named %s already exists in %s\n" % (name, conflicting_project.src)
        raise Exception(mess)

    if os.path.exists(path):
        if skip_if_exists:
            LOGGER.debug("Found %s in %s, skipping" % (name, path))
        else:
            mess  = "Could not add project %s from %s\n" % (name, url)
            mess += "Path %s already exists\n" % path
            mess += "Please choose another name or another path"
            raise Exception(mess)
    else:
        LOGGER.info("Git clone: %s -> %s", url, path)
        git = qisrc.git.Git(path)
        git.clone(url)
    if not name in p_names:
        worktree.add_project(name, path)
