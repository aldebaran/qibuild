## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Set of tools to parse qisrc manifests

"""

import copy
import functools

import qisys.sh
import qisys.qixml
import qisrc.git_config
import qisrc.groups

class ManifestError(Exception):
    pass


class Manifest(object):
    def __init__(self, manifest_xml):
        self.manifest_xml = manifest_xml
        self.repos = list()
        self.remotes = list()
        self.groups = qisrc.groups.Groups()
        self.load()

    # pylint: disable-msg=E0213
    def change_config(func):
        """ Decorator for every function that changes the configuration """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            # pylint: disable-msg=E1102
            res = func(self, *args, **kwargs)
            self.dump()
            # mandatory to re-compute project.remote,
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

        for remote in self.remotes:
            remote.parse_url()

        for repo in self.repos:
            if not repo.remote_name:
                repo.remote_name = "origin"
            if not repo.default_branch:
                repo.default_branch = "master"
            self.set_remote(repo)

    def set_remote(self, repo):
        """ Set the remote of a repo from the list.
        Assume all the remotes have already been read

        """
        matching_remote = self.get_remote(repo.remote_name)
        if not matching_remote:
            raise ManifestError("No matching remote: %s for repo %s" %
                                (repo.remote_name, repo.project))
        repo.remote = copy.copy(matching_remote)
        repo.remote.url = matching_remote.prefix + repo.project

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

            try:
                project_names = self.groups.projects(group)
            except qisrc.groups.GroupError as e:
                raise ManifestError(str(e))
            for project_name in project_names:
                matching_repo = self.get_repo(project_name)
                if matching_repo:
                    repos[project_name] = matching_repo
                else:
                    raise ManifestError("""When reading group {0}:
No such project: {1}
""".format(group, project_name))
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

    # Following methods are mainly use for testing,
    # but could be useful for othe use cases anyway

    @change_config
    def add_remote(self, name, url, review=False):
        """ Add a new remote to the manifest. """
        remote = qisrc.git_config.Remote()
        remote.name = name
        remote.url = url
        remote.review = review
        self.remotes.append(remote)

    @change_config
    def add_repo(self, project_name, src, remote_name=None,
                 default_branch="master"):
        """ Add a new repo to the manifest. """
        repo = RepoConfig()
        repo.project = project_name
        repo.src = src
        repo.remote_name = remote_name
        repo.default_branch = default_branch
        self.repos.append(repo)

    @change_config
    def remove_repo(self, project_name):
        """ Remove a repo from the manifest """
        matching_repo = self.get_repo(project_name)
        if not matching_repo:
            raise Exception("No such repo:", project_name)
        self.repos.remove(matching_repo)

    @change_config
    def configure_group(self, name, projects):
        """ Configure a group """
        self.groups.configure_group(name, projects)

class RepoConfig(object):
    def __init__(self):
        self.src = None
        self.project = None
        self.default_branch = None
        self.remote = None
        self.remote_name = None

    @property
    def review(self):
        return self.remote and self.remote.review

    def __repr__(self):
        res = "<Repo %s in %s" %  (self.project, self.src)
        if self.default_branch:
            res += " default: %s" % self.default_branch
        if not self.remote:
            res += " (no remote yet)"
        if self.review:
            res += " (review)"
        res += ">"
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
        remote = qisrc.git_config.Remote()
        parser = qisrc.git_config.RemoteParser(remote)
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
            parser = qisrc.git_config.RemoteParser(remote)
            remote_elem = parser.xml_elem()
            elem.append(remote_elem)

    def _write_groups(self, elem):
        parser = qisrc.groups.GroupsParser(self.target.groups)
        elem.append(parser.xml_elem())

class RepoConfigParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(RepoConfigParser, self).__init__(target)
        self._ignore = ["remote", "review"]
        self._required = ["project"]

    # the 'remote' XML attribute matches an attribute named
    # 'remote_name' in the RepoConfig class
    def _parse_attributes(self):
        self.target.project = self._root.get("project")
        if not self.target.project:
            raise ManifestError("Missing 'project' attribute")
        self.target.src = self._root.get("src")
        self.target.default_branch = self._root.get("branch", "master")
        self.target.remote_name = self._root.get("remote", "origin")

    def _write_remote_name(self, elem):
        if self.target.remote_name:
            elem.set("remote", self.target.remote_name)
