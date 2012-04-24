## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to qibuild manifests

"""

import posixpath

import qibuild.sh
import qixml

def git_url_join(remote, name):
    """ Join a remote ref with a name

    """
    if remote.startswith("http://"):
        return posixpath.join(remote, name)
    if remote.startswith("ssh://"):
        return posixpath.join(remote, name)
    if "@" in remote:
        return remote + ":" + name
    return posixpath.join(remote, name)

class Manifest():
    def __init__(self, xml_path):
        # Used to check that we do not defined two projects
        # with the same path
        self._paths = dict()
        self.tree = qixml.read(xml_path)
        self.projects = list()
        self.remotes = list()
        self.parse_remotes()
        self.parse_projects()

    def parse_remotes(self):
        remote_elems = self.tree.findall("remote")
        for remote_elem in remote_elems:
            remote = Remote()
            remote.parse(remote_elem)
            self.remotes.append(remote)

    def get_remote(self, name="origin"):
        matches = [r for r in self.remotes if r.name == name]
        if matches:
            return matches[0]
        return None

    def get_project(self, name):
        matches = [p for p in self.projects if p.name == name]
        if matches:
            return matches[0]
        return None

    def parse_projects(self):
        project_elems = self.tree.findall("project")
        for project_elem in project_elems:
            project = Project()
            project.parse(project_elem)
            p_remote = project.remote
            remote = self.get_remote(p_remote)
            if not remote:
                continue
            if not project.revision:
                project.revision = remote.revision
            project.fetch_url = git_url_join(remote.fetch, project.name)
            if project.review:
                project.review_url = git_url_join(remote.review, project.name)
            conflicting_name = self._paths.get(project.path)
            if conflicting_name:
                mess  = "Found two projects with the same path: %s\n" % project.path
                mess += "%s and %s" % (project.name, conflicting_name)
                raise Exception(mess)
            self._paths[project.path] = project.name
            self.projects.append(project)


class Project:
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
            self.path = qibuild.sh.to_posix_path(xml_path)
            self.path = posixpath.normpath(xml_path)
        self.revision = xml_element.get("revision")
        self.worktree_name = xml_element.get("worktree_name")
        self.review = qixml.parse_bool_attr(xml_element, "review")
        self.remote = xml_element.get("remote")
        if not self.remote:
            self.remote = "origin"


class Remote:
    def __init__(self):
        self.name = None
        self.fetch = None
        self.review = None
        self.revision = None

    def parse(self, xml_element):
        self.name = xml_element.get("name")
        if not self.name:
            self.name = "origin"
        self.fetch = qixml.parse_required_attr(xml_element, "fetch")
        self.review = xml_element.get("review")
        self.revision = xml_element.get("revision")
        if not self.revision:
            self.revision = "master"
