## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

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


