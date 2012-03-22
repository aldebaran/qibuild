## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to qibuild manifests

"""

import posixpath
import qibuild.xml

def git_url_join(remote, name):
    """ Join a remote ref with a name

    """
    if remote.startswith("http://"):
        return posixpath.join(remote, name)
    if "@" in remote:
        return remote + ":" + name
    return posixpath.join(remote, name)

class Manifest():
    def __init__(self, xml_path):
        self.tree = qibuild.xml.parse_xml(xml_path)
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
            if not p_remote:
                p_remote = "origin"
            remote = self.get_remote(p_remote)
            if not remote:
                continue
            project.fetch_url = git_url_join(remote.fetch, project.name)
            self.projects.append(project)


class Project(qibuild.xml.XMLModel):
        name = qibuild.xml.StringField()
        path = qibuild.xml.StringField()
        review = qibuild.xml.BoolField()
        remote = qibuild.xml.StringField()


class Remote(qibuild.xml.XMLModel):
        name = qibuild.xml.StringField()
        fetch = qibuild.xml.StringField()
        review = qibuild.xml.StringField()




def sync_worktree(worktree, manifest_location):
    """ Synchronize a worktree using a manifest location

    """




