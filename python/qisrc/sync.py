## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with a manifest

"""
import os
import logging

import qisrc.manifest
import qisrc.git

LOGGER = logging.getLogger(__name__)

def manifest_from_git(worktree, manifest_git_url):
    """ Synchronize a worktree given a manifest git url.

    The url should point to a git repository containing a
    'default.xml' file, ala repo

    """
    clone_project(worktree, manifest_git_url,
                  skip_if_exists=True)
    manifest = worktree.get_project("manifest")
    git = qisrc.git.open(manifest.src)
    git.pull()
    default_xml = os.path.join(manifest.src, "default.xml")
    return default_xml


def sync_worktree(worktree, rebase=True, manifest_locations=None):
    """ Synchronize a worktree.
    :param manifest_locations: If given, must be a
        list of paths to xml files

    """
    if manifest_locations is None:
        manifest_locations = list()
    # First clone every missing repository using the manifest locations
    for manifest_location in manifest_locations:
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
    for git_project in worktree.git_projects:
        git = qisrc.git.open(git_project.src)
        if rebase:
            git.pull("--rebase")
        else:
            git.pull()


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

    if os.path.exists(path):
        if skip_if_exists:
            LOGGER.info("Found %s in %s, skipping" % (name, path))
        else:
            mess  = "Could not add project %s from %s\n" % (name, url)
            mess += "%s already exists\n" % path
            mess += "Please choose another name or another path"
            raise Exception(mess)

    LOGGER.info("Git clone: %s -> %s", url, path)
    git = qisrc.git.Git(path)
    git.clone(url)

    worktree.add_project(name, path)
