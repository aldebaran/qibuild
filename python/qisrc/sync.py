## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
from qisrc.manifest import sync_worktree

""" Handling synchronistation of a worktree with a manifest

"""
import os
import logging

import qisrc.manifest
import qisrc.git

LOGGER = logging.getLogger(__name__)

def sync_worktree_from_git(worktree, manifest_git_url):
    clone_project(worktree, manifest_git_url,
                  name="manifest",
                  path="manifest",
                  skip_if_exists=True)
    manifest = worktree.get_project("manifest")
    git = qisrc.git.open(manifest.src)
    git.pull()
    default_xml = os.path.join(manifest.src, "default.xml")
    sync_worktree(worktree, default_xml)


def sync_worktree(worktree, manifest_location):
    manifest = qisrc.manifest.Manifest(manifest_location)
    for project in manifest.projects:
        p_name = project.name
        p_url = project.fetch_url
        p_path = project.path
        clone_project(worktree, p_url,
                      name=p_name,
                      path=p_path,
                      skip_if_exists=True)


def clone_project(worktree, url,
                  name=None,
                  path=None,
                  skip_if_exists=False):
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
