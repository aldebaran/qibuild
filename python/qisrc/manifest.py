# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Set of tools to parse qisrc manifests

"""

import copy
import functools
import StringIO

import qisys.sh
import qisys.qixml
import qisrc.git_config
import qisrc.groups


class ManifestError(Exception):
    pass


class Manifest(object):
    def __init__(self, manifest_xml, review=True):
        self.manifest_xml = manifest_xml
        self.review = review
        self.repos = list()
        self.remotes = list()
        self.default_branch = None
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
        project_names = list()
        self.repos = list()
        self.remotes = list()
        self.import_manifest = list()
        self.groups = qisrc.groups.Groups()
        root = qisys.qixml.read(self.manifest_xml).getroot()
        parser = ManifestParser(self)
        parser.parse(root)

        for repo in self.repos:
            if repo.project in project_names:
                raise ManifestError("%s found twice" % repo.project)
            project_names.append(repo.project)

        for remote in self.remotes:
            if remote.review and not self.review:
                continue
            remote.parse_url()

        review_remotes = list()
        for remote in self.remotes:
            if remote.review:
                review_remotes.append(remote)

        if len(review_remotes) > 1:
            mess = """ \
Only one remote can be configured with review="true", found {0}
""".format(len(review_remotes))
            raise ManifestError(mess)

        for import_manifest in self.import_manifest:
            self.set_remote(import_manifest, import_manifest.default_remote_name)

        srcs = dict()
        for repo in self.repos:
            if repo.src in srcs:
                mess = """ \
Found two projects sharing the same sources:
* {0}
* {1}
""".format(srcs[repo.src], repo)
                raise ManifestError(mess)

            for remote_name in repo.remote_names:
                self.set_remote(repo, remote_name)

            srcs[repo.src] = repo

    def set_remote(self, repo, remote_name):
        """ Set the remote of a repo from the list.
        Assume all the remotes have already been read

        """
        matching_remote = self.get_remote(remote_name)
        if not matching_remote:
            raise ManifestError("No matching remote: %s for repo %s" %
                                (remote_name, repo.project))
        if matching_remote.review and not self.review:
            return
        remote = copy.copy(matching_remote)
        remote.url = matching_remote.prefix + repo.project
        # Default branch can be set on the remote, or even
        # on the manifest itself
        if repo.default_branch is None:
            if self.default_branch:
                repo.default_branch = self.default_branch
            else:
                repo.default_branch = remote.default_branch
        if remote.name == repo.default_remote_name:
            remote.default = True
        # Make sure default_branch is None, even if it was
        # set from the remote or the manifest
        if repo.fixed_ref:
            repo.default_branch = None
        repo.remotes.append(remote)

    def dump(self):
        """ write the xml configuration file """
        parser = ManifestParser(self)
        xml_elem = parser.xml_elem()
        qisys.qixml.write(xml_elem, self.manifest_xml)

    def get_repos(self, groups=None, get_all=False):
        """ Get the repositories inside the given group

        * If there is a default group, returns projects
          from the default group, unless get_all is True,
          then return all the projects

        """
        default_group = self.groups.default_group
        if groups is None:
            if default_group and not get_all:
                groups = [default_group.name]
            else:
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
    # but could be useful for other use cases anyway

    @change_config
    def add_remote(self, name, url, review=False):
        """ Add a new remote to the manifest. """
        remote = qisrc.git_config.Remote()
        remote.name = name
        remote.url = url
        remote.review = review
        self.remotes.append(remote)

    @change_config
    def add_repo(self, project_name, src, remote_names,
                 default_branch="master"):
        """ Add a new repo to the manifest. """
        repo = RepoConfig()
        repo.project = project_name
        repo.src = src
        repo.remote_names = remote_names
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
    def configure_group(self, name, projects, default=False):
        """ Configure a group """
        self.groups.configure_group(name, projects, default=default)

    @change_config
    def remove_group(self, name):
        """ Remove a group from the manifest """
        self.groups.remove_group(name)


def from_git_repo(git_repo, ref):
    git = qisrc.git.Git(git_repo)
    rc, out = git.call("cat-file", "-p", ref + "^{tree}", raises=False)
    if rc != 0:
        return None
    lines = out.splitlines()
    manifest_line = None
    for line in lines:
        if line.endswith("\tmanifest.xml"):
            manifest_line = line
    if not manifest_line:
        return None
    manifest_blob_sha1 = manifest_line.split()[2]
    rc, as_string = git.call("cat-file", "-p", manifest_blob_sha1, raises=False)
    if rc != 0:
        return None
    source = StringIO.StringIO(as_string)
    return Manifest(source)


class RepoConfig(object):
    def __init__(self):
        self.src = None
        self.project = None
        self.default_branch = None
        self.fixed_ref = None
        self.default_remote_name = None
        self.remotes = list()
        self.remote_names = None

    @property
    def review_remote(self):
        for remote in self.remotes:
            if remote.review:
                return remote

    @property
    def default_remote(self):
        """ Return the remote that will be used to clone
        the project

        """
        for remote in self.remotes:
            if remote.default:
                return remote

    @property
    def clone_url(self):
        return self.default_remote.url

    @property
    def urls(self):
        return [remote.url for remote in self.remotes]

    @property
    def review(self):
        return self.review_remote is not None

    def __repr__(self):
        res = "<Repo %s in %s" % (self.project, self.src)
        if self.default_branch:
            res += " default: %s" % self.default_branch
        if self.review:
            res += " (review)"
        if self.fixed_ref:
            res += " on %s" % self.fixed_ref
        res += ">"
        return res


class ImportManifest(object):
    def __init__(self):
        self.project = None
        self.default_branch = None
        self.branch = None
        self.fixed_ref = None
        self.default_remote_name = None
        self.remotes = list()
        self.remote_names = None

    def __repr__(self):
        res = "<Import manifest %s" % self.project
        if self.branch:
            res += " branch: %s" % self.branch
        if self.fixed_ref:
            res += " on %s" % self.fixed_ref
        res += ">"
        return res

##
# parsing


class ManifestParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ManifestParser, self).__init__(target)
        self._ignore = ["manifest_xml", "review"]

    def _parse_branch(self, elem):
        self.target.default_branch = elem.get("default")

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

    def _parse_import(self, elem):
        import_manifest = ImportManifest()
        parser = ImportManifestParser(import_manifest)
        parser.parse(elem)
        self.target.import_manifest.append(import_manifest)

    def _parse_groups(self, elem):
        parser = qisrc.groups.GroupsParser(self.target.groups)
        parser.parse(elem)

    def _write_branch(self, elem):
        elem.set("default", self.target.default_branch)

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


class ImportManifestParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ImportManifestParser, self).__init__(target)
        self._ignore = ["review_remote",
                        "default_remote_name",
                        "clone_url",
                        "review",
                        "urls",
                        "remotes"]
        self._required = ["manifest"]

    # the 'remote' XML attribute matches an attribute named
    # 'remote_name' in the RepoConfig class
    def _parse_attributes(self):
        self.target.project = self._root.get("manifest")
        if not self.target.project:
            raise ManifestError("Missing 'manifest' attribute")

        self.target.branch = self._root.get("branch")
        self.target.fixed_ref = self._root.get("ref")
        if self.target.fixed_ref and self.target.branch:
            mess = "Error when parsing project %s\n" % self.target.project
            mess += "'branch' and 'ref' are mutually exclusive"
            raise ManifestError(mess)

        remote_names = self._root.get("remotes")
        if remote_names is None:
            raise ManifestError("Missing 'remotes' attribute")
        if remote_names == "":
            raise ManifestError("Empty 'remotes' attribute")
        remote_names = remote_names.split()
        self.target.remote_names = remote_names
        self.target.default_remote_name = self._root.get("default_remote")
        if not self.target.default_remote_name:
            self.target.default_remote_name = remote_names[0]


class RepoConfigParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(RepoConfigParser, self).__init__(target)
        self._ignore = ["review_remote",
                        "default_remote_name",
                        "clone_url",
                        "review",
                        "urls",
                        "remotes"]
        self._required = ["project"]

    # the 'remote' XML attribute matches an attribute named
    # 'remote_name' in the RepoConfig class
    def _parse_attributes(self):
        self.target.project = self._root.get("project")
        if not self.target.project:
            raise ManifestError("Missing 'project' attribute")
        src = self._root.get("src")
        if src is None:
            src = self.target.project.replace(".git", "")
        self.target.src = src

        self.target.default_branch = self._root.get("branch")
        self.target.fixed_ref = self._root.get("ref")
        if self.target.fixed_ref and self.target.default_branch:
            mess = "Error when parsing project %s\n" % self.target.project
            mess += "'branch' and 'ref' are mutually exclusive"
            raise ManifestError(mess)
        remote_names = self._root.get("remotes")
        if remote_names is None:
            raise ManifestError("Missing 'remotes' attribute")
        if remote_names == "":
            raise ManifestError("Empty 'remotes' attribute")
        remote_names = remote_names.split()
        self.target.remote_names = remote_names
        self.target.default_remote_name = self._root.get("default_remote")
        if not self.target.default_remote_name:
            self.target.default_remote_name = remote_names[0]

        for upstream_elem in self._root.findall("upstream"):
            name = qisys.qixml.parse_required_attr(upstream_elem, "name")
            url = qisys.qixml.parse_required_attr(upstream_elem, "url")
            upstream_remote = qisrc.git_config.Remote()
            upstream_remote.name = name
            upstream_remote.url = url
            self.target.remotes.append(upstream_remote)

    def _write_remote_names(self, elem):
        elem.set("remotes", " ".join(self.target.remote_names))

    def _write_fixed_ref(self, elem):
        if self.target.fixed_ref:
            elem.set("ref", self.target.fixed_ref)

    def _write_default_branch(self, elem):
        if self.target.default_branch:
            elem.set("branch", self.target.default_branch)
