## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to parse qisrc manifests

"""

import functools
import posixpath

import qisys.sh
import qisys.qixml
import qisrc.worktree
import qisrc.groups

class ManifestError(Exception):
    pass


def git_url_join(remote, name):
    """Join a remote ref with a name."""
    if remote.startswith(("http://", "ssh://")):
        return posixpath.join(remote, name)
    if "@" in remote:
        return remote + ":" + name
    return posixpath.join(remote, name)




class Manifest(object):
    def __init__(self, manifest_xml):
        self.manifest_xml = manifest_xml
        self.repos = list()
        self.remotes = list()
        self.groups = qisrc.groups.Groups()
        self.load()

    def change_config(func):
        """ Decorator for every function that changes the configuration """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            self.dump()
            # mandatory to re-compute project.remote_url,
            # project.review and so on
            self.load()
            return res
        return new_func

    def load(self):
        """ (re)-parse the xml configuration file """
        self.repos = list()
        self.remotes = list()
        self.groups = qisrc.groups.Groups()
        root = qisys.qixml.read(self.manifest_xml).getroot()
        parser = ManifestParser(self)
        parser.parse(root)

        for repo in self.repos:
            if not repo.remote:
                repo.remote = "origin"
            matching_remote = self.get_remote(repo.remote)
            if matching_remote:
                repo.remote_url = git_url_join(matching_remote.url, repo.project)
                if matching_remote.review:
                    repo.review = True
            else:
                raise ManifestError("No matching remote: %s for repo %s" %
                                  (repo.remote, repo.project))
    def dump(self):
        """ write the xml configuration file """
        parser = ManifestParser(self)
        xml_elem = parser.xml_elem()
        qisys.qixml.write(xml_elem, self.manifest_xml)

    def get_repos(self, groups=None):
        """ Get the repositories inside the given group
        Retrun all repositories when no group is given

        """
        if not groups:
            return self.repos

        repos = dict()
        for group in groups:
            project_names = self.groups.projects(group)
            for project_name in project_names:
                matching_repo = self.get_repo(project_name)
                if matching_repo:
                    repos[project_name] = matching_repo
        return repos.values()

    def get_repo(self, project):
        """ Get a repository given the project name (foo/bar.git) """
        for repo in self.repos:
            if repo.project == project:
                return repo

    def get_remote(self, name):
        """ Get a remote given the name """
        for remote in self.remotes:
            if remote.name == name:
                return remote

    @change_config
    def add_remote(self, name, url, review=False):
        """ Add a new remote to the manifest. """
        remote = qisrc.worktree.Remote()
        remote.name = name
        remote.url = url
        self.remotes.append(remote)

    @change_config
    def add_repo(self, project_name, src, remote_name=None,
                 default_branch="master"):
        """ Add a new repo to the manifest. """
        repo = RepoConfig()
        repo.project = project_name
        repo.src = src
        repo.remote = remote_name
        repo.default_branch = default_branch
        self.repos.append(repo)

    @change_config
    def remove_repo(self, project_name):
        """ Remove a repo from the manifest """
        matching_repo = self.get_repo(project_name)
        if not matching_repo:
            raise Exception("No such repo:", project_name)
        self.repos.remove(matching_repo)

class RepoConfig(object):
    def __init__(self):
        self.remote = None
        self.src = None
        self.project = None
        self.default_branch = None
        self.remote_url = None
        self.review = False


    def __repr__(self):
        res = "<Project %s in %s" %  (self.project, self.src)
        if self.default_branch:
            res += " default: %s>" % self.default_branch
        return res

##
# parsing

class ManifestParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ManifestParser, self).__init__(target)


    def _parse_repo(self, elem):
        repo_config = RepoConfig()
        parser = RepoConfigParser(repo_config)
        parser.parse(elem)
        self.target.repos.append(repo_config)

    def _parse_remote(self, elem):
        remote = qisrc.worktree.Remote()
        parser = qisrc.worktree.RemoteParser(remote)
        parser.parse(elem)
        self.target.remotes.append(remote)

    def _parse_groups(self, elem):
        parser = qisrc.groups.GroupsParser(self.target.groups)
        parser.parse(elem)

    def _write_repos(self, elem):
        for repo_config in self.target.repos:
            parser = RepoConfigParser(repo_config)
            repo_elem = parser.xml_elem(node_name="repo")
            elem.append(repo_elem)

    def _write_remotes(self, elem):
        for remote in self.target.remotes:
            parser = qisrc.worktree.RemoteParser(remote)
            remote_elem = parser.xml_elem()
            elem.append(remote_elem)

class RepoConfigParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(RepoConfigParser, self).__init__(target)
        self._ignore = ["remote_url", "review"]
        self._required = ["project"]
