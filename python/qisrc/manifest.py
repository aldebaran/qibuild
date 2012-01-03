## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to handle source manifests

"""

# FIXME: this code is very similar to qitoolchain.feed

import os
import qitoolchain
from xml.etree import ElementTree

def raise_parse_error(tree, manifest, message):
    """ Raise a nice parsing error about the given
    tree element

    """
    as_str = ElementTree.tostring(tree)
    mess  = "Error when parsing manifest: '%s'\n" % manifest
    mess += "Could not parse:\t%s\n" % as_str
    mess += message
    raise Exception(mess)


def tree_from_manifest(manifest_location):
    """ Returns an ElementTree object from a
    manifest location

    """
    fp = None
    tree = None
    try:
        if os.path.exists(manifest_location):
            fp = open(manifest_location, "r")
        else:
            fp = qitoolchain.remote.open_remote_location(manifest_location)
        tree = ElementTree.ElementTree()
        tree.parse(fp)
    except Exception, e:
        mess  = "Could not parse %s\n" % manifest_location
        mess += "Error was: \n"
        mess += str(e)
        raise Exception(mess)
    finally:
        if fp:
            fp.close()
    return tree


class ManifestParser:
    """ A class to handle manifest parsing

    """
    def __init__(self):
        # A dict project_name -> url used to only one URL
        # per project
        self.projects = dict()

    def parse(self, manifest):
        """ Recursively parse the manifest, filling self.projects

        """
        tree = tree_from_manifest(manifest)
        project_trees = tree.findall("project")
        for project_tree in project_trees:
            project_name = project_tree.get("name")
            if not project_name:
                raise_parse_error(project_tree, manifest, "name attribute is required")
            project_url = project_tree.get("url")
            if not project_url:
                raise_parse_error(project_tree, manifest, "url attribute is required")
            self.projects[project_name] = project_url
        manifest_trees = tree.findall("manifest")
        for manifest_tree in manifest_trees:
            manifest_url = manifest_tree.get("url")
            if manifest_url:
                self.parse(manifest_url)


def  parse_manifest(manifest):
    """ Parse a manifest, cloning required repositories
    while doing so

    :param wt: the worktree
    :param manifest: a manifest location (a file path or an url)
    """
    parser = ManifestParser()
    parser.parse(manifest)
    return parser.projects


