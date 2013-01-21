## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to parse qisrc manifests

"""

import os
import posixpath

import qisys.sh
import qixml

import qisys.xml_parser

class NoManifest(Exception):
    def __init__(self, worktree):
        self.worktree = worktree
    def __str__(self):
        res  = "Could not find any manifest project for worktree in %s \n" % \
            self.worktree.root
        res += "Try calling `qisrc init MANIFEST_URL`"
        return res

def git_url_join(remote, name):
    """Join a remote ref with a name."""
    if remote.startswith(("http://", "ssh://")):
        return posixpath.join(remote, name)
    if "@" in remote:
        return remote + ":" + name
    return posixpath.join(remote, name)

def load(manifest_xml):
    """Load a manifest XML file."""
    manifest = Manifest(manifest_xml)
    manifest.parse()
    merge_projects(manifest)
    return manifest

def merge_projects(manifest):
    """Merge recursively the projects coming from the sub manifests."""
    for sub_manifest in manifest.sub_manifests:
        merge_projects(sub_manifest)
        manifest.projects.extend(sub_manifest.projects)

class Manifest(qisys.xml_parser.RootXMLParser):
    """ A class to represent the contents of a manifest XML
    file.

    Do not use instanciate directly, use :py:meth:`load` instead.

    """
    def __init__(self, xml_path):
        self.xml_path = xml_path
        tree = qixml.read(xml_path)
        root = tree.getroot()

        qisys.xml_parser.RootXMLParser.__init__(self, root)

        self.remotes = dict()
        self.projects = list()
        self.sub_manifests = list()

        # Used to track conflicts
        self._paths = dict()

    def _parse_remote(self, element):
        remote = Remote(element)
        remote.parse()
        self.remotes[remote.name] = remote

    def _parse_project(self, element):
        project = Project(element)
        project.parse()
        self.projects.append(project)

    def _parse_manifest(self, element):
        url = element.get("url")
        if not url:
            return

        dirname = os.path.dirname(self.xml_path)
        submanifest_path = os.path.join(dirname, url)

        submanifest = Manifest(submanifest_path)
        submanifest.parse()
        self.sub_manifests.append(submanifest)

    def _parse_epilogue(self):
        for project in self.projects:
            update_project(project, self.remotes, self._paths)

def update_project(project, remotes, paths):
    """ Update the project list, setting project.revision,
    project.fetch_url and so on, using the already parsed remotes

    """
    remote = remotes.get(project.remote)
    if not remote:
        return
    if not project.revision:
        project.revision = remote.revision
    project.fetch_url = git_url_join(remote.fetch, project.name)
    if project.review:
        if not remote.review:
            mess = """ \
Project {project.name} was configured for review
but the associated remote ({remote.name}) has
no review url set.\
"""
            mess = mess.format(remote=remote, project=project)
            raise Exception(mess)

        project.review_url = git_url_join(remote.review, project.name)
    conflicting_name = paths.get(project.path)
    if conflicting_name:
        mess  = "Found two projects with the same path: %s\n" % project.path
        mess += "%s and %s" % (project.name, conflicting_name)
        raise Exception(mess)
    paths[project.path] = project.name

class Project(qisys.xml_parser.RootXMLParser):
    """Wrapper for the <project> tag inside a manifest XML file."""
    def __init__(self, root):
        qisys.xml_parser.RootXMLParser.__init__(self, root)
        self.name = None
        self.path = None
        self.review = False
        self.remote = "origin"
        self.revision = None
        # Set during manifest parsing
        self.fetch_url = None
        self.review_url = None

    def _post_parse_attributes(self):
        self.check_needed("name")
        if not self.path:
            self.path = self.name.replace(".git", "")
        else:
            self.path = posixpath.normpath(self.path)

    def __repr__(self):
        res = "<Project %s remote: %s fetch: %s review:%s>" % \
            (self.name, self.remote, self.fetch_url, self.review_url)
        return res

class Remote(qisys.xml_parser.RootXMLParser):
    """Wrapper for the <remote> tag inside a manifest XML file."""
    def __init__(self, root):
        qisys.xml_parser.RootXMLParser.__init__(self, root)
        self.name = "origin"
        self.fetch = None
        self.review = None
        self.revision = "master"

    def _post_parse_attributes(self):
        self.check_needed("fetch")

    def __repr__(self):
        res = "<Remote %s fetch: %s on %s, review:%s>" % \
            (self.name, self.fetch, self.revision, self.review)
        return res
