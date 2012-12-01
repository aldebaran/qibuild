## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to parse qisrc manifests

"""

import os
import posixpath

import qisys.sh
import qixml

class NoManifest(Exception):
    def __init__(self, worktree):
        self.worktree = worktree
    def __str__(self):
        res  = "Could not find any manifest project for worktree in %s \n" % \
            self.worktree.root
        res += "Try calling `qisrc init MANIFEST_URL`"
        return res

def git_url_join(remote, name):
    """ Join a remote ref with a name

    """
    if remote.startswith(("http://", "ssh://")):
        return posixpath.join(remote, name)
    if "@" in remote:
        return remote + ":" + name
    return posixpath.join(remote, name)

def load(manifest_xml):
    """ Load a manifest XML file

    """
    manifest = Manifest()
    manifest.parse(manifest_xml)
    res = manifest
    merge_projects(manifest)
    return res


def merge_projects(manifest):
    """ Merge recursively the projects coming from the sub manifests,
    filtering out what is inside the blacklist

    """
    for sub_manifest in manifest.sub_manifests:
        merge_projects(sub_manifest)
        for sub_project in sub_manifest.projects:
            if sub_project.name in manifest.blacklist:
                continue
            manifest.projects.append(sub_project)

class Manifest():
    """ A class to represent the contents of a manifest XML
    file.

    Do not use instanciate directly, use :py:meth:`load` instead.

    """
    def __init__(self):
        self.remotes = dict()
        self.projects = list()
        self.blacklist = list()
        self.sub_manifests = list()
        self.xml_path = None

        # Used to track conflicts
        self._paths = dict()

    def parse(self, xml_path):
        """ Recursive function. This is also called on each
        sub manifest, so that self.sub_manifests contains
        fully initialized Manifest() objects when this function
        returns

        """
        self.xml_path = xml_path
        tree = qixml.read(xml_path)

        remotes = parse_remotes(tree)
        for remote in remotes:
            self.remotes[remote.name] = remote

        projects = parse_projects(tree)
        self.projects.extend(projects)

        blacklists = parse_blacklists(tree)
        self.blacklist.extend(blacklists)

        sub_manifests = parse_manifests(tree, xml_path)
        self.sub_manifests.extend(sub_manifests)

        self.update_projects()

    def update_projects(self):
        """ Update the project list, setting project.revision,
        project.fetch_url and so on, using the already parsed remotes

        """
        for project in self.projects:
            remote = self.remotes.get(project.remote)
            if not remote:
                continue
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
            conflicting_name = self._paths.get(project.path)
            if conflicting_name:
                mess  = "Found two projects with the same path: %s\n" % project.path
                mess += "%s and %s" % (project.name, conflicting_name)
                raise Exception(mess)
            self._paths[project.path] = project.name

    def __repr__(self):
        res = "<Manifest from %s\n" % self.xml_path
        res += "   remotes: %s\n" % self.remotes
        res += "   projects: %s\n" % self.projects
        return res

def parse_manifests(tree, xml_path):
    sub_manifests = list()
    manifest_elems = tree.findall("manifest")
    for manifest_elem in manifest_elems:
        manifest_url = manifest_elem.get("url")
        if manifest_url:
            dirname = os.path.dirname(xml_path)
            sub_manifest_xml = os.path.join(dirname, manifest_url)
            sub_manifest = Manifest()
            sub_manifest.xml_path = sub_manifest_xml
            sub_manifest.parse(sub_manifest.xml_path)
            sub_manifests.append(sub_manifest)

    return sub_manifests


class Project:
    """ Wrapper for the <project> tag inside a manifest
    XML file

    """
    def __init__(self):
        self.name = None
        self.path = None
        self.review = False
        self.remote = None
        self.revision = None
        # Set during manifest parsing
        self.fetch_url = None
        self.review_url = None

    def parse(self, xml_element):
        self.name = qixml.parse_required_attr(xml_element, "name")
        xml_path = xml_element.get("path")
        if not xml_path:
            self.path = self.name.replace(".git", "")
        else:
            self.path = qisys.sh.to_posix_path(xml_path)
            self.path = posixpath.normpath(xml_path)
        self.revision = xml_element.get("revision")
        self.worktree_name = xml_element.get("worktree_name")
        self.review = qixml.parse_bool_attr(xml_element, "review")
        self.remote = xml_element.get("remote", default="origin")

    def __repr__(self):
        res = "<Project %s remote: %s fetch: %s review:%s>" % \
            (self.name, self.remote, self.fetch_url, self.review_url)
        return res

def parse_projects(tree):
    projects = list()
    project_elems = tree.findall("project")
    for project_elem in project_elems:
        project = Project()
        project.parse(project_elem)
        projects.append(project)

    return projects


class Remote:
    """ Wrapper for the <remote> tag inside a manifest
    XML file

    """
    def __init__(self):
        self.name = None
        self.fetch = None
        self.review = None
        self.revision = None

    def parse(self, xml_element):
        self.name = xml_element.get("name", default="origin")
        self.fetch = qixml.parse_required_attr(xml_element, "fetch")
        self.review = xml_element.get("review")
        self.revision = xml_element.get("revision", default="master")

    def __repr__(self):
        res = "<Remote %s fetch: %s on %s, review:%s>" % \
            (self.name, self.fetch, self.revision, self.review)
        return res

def parse_remotes(tree):
    remotes = list()
    remote_elems = tree.findall("remote")
    for remote_elem in remote_elems:
        remote = Remote()
        remote.parse(remote_elem)
        remotes.append(remote)

    return remotes

def parse_blacklists(tree):
    blacklists = list()
    blacklist_elems = tree.findall("blacklist")
    for blacklist_elem in blacklist_elems:
        name = blacklist_elem.get("name")
        if name:
            blacklists.append(name)
    return blacklists

