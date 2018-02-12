# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Handling synchronization of a worktree with some manifests

"""

import os

from qisys.qixml import etree
from qisys import ui
import qisys.qixml
import qisrc.git
import qisrc.manifest


class WorkTreeSyncer(object):
    """ Handle the manifests of a worktree

    Stores the git url of the manifests and the groups that
    should be used, synchronizes the local manifests with the git
    worktree

    """

    def __init__(self, git_worktree):
        self.git_worktree = git_worktree
        # Read manifest configuration now, before any
        self.manifest = LocalManifest()
        self.read_manifest_config()
        self.old_repos = list()
        self.new_repos = list()

    def sync(self):
        """" Synchronize with a remote manifest:
        * clone missing repos
        * move repos that needs to be moved
        * reconfigure remotes and default branches
        * synchronizes build profiles
        :returns: True in case of success, False otherwise

        """
        # backup old repos configuration now, so that
        # we know what to sync
        self.old_repos = self.get_old_repos()
        return self.sync_repos()

    @property
    def manifest_xml(self):
        # it's manifests (plural) for backward-compatible reasons
        manifest_xml_path = os.path.join(self.git_worktree.root, ".qi", "manifests.xml")
        if not os.path.exists(manifest_xml_path):
            with open(manifest_xml_path, "w") as fp:
                fp.write("<manifest />")
        return manifest_xml_path

    @property
    def manifest_repo(self):
        # the repo is always in manifests/default for backward-compatible reasons
        res = os.path.join(self.git_worktree.root, ".qi", "manifests", "default")
        if not os.path.exists(res):
            qisys.sh.mkdir(res, recursive=True)
            git = qisrc.git.Git(res)
            git.init()
            manifest_xml = os.path.join(res, "manifest.xml")
            with open(manifest_xml, "w") as fp:
                fp.write("<manifest />")
            git.add(".")
            git.commit("-m", "initial commit")
        return res

    def sync_repos(self, force=False):
        """ Update the manifest, inspect changes, and updates the
        git worktree accordingly

        """
        res = True
        ui.info(ui.green, ":: Updating manifest ...")
        ui.info(ui.green, "* ",
                ui.reset, ui.bold, "(%s) " % self.manifest.branch,
                end="")
        if self.manifest.groups:
            ui.info("groups", ", ".join(self.manifest.groups))
        else:
            ui.info()
        self._sync_manifest()
        self.new_repos = self.read_remote_manifest()
        res = self._sync_repos(self.old_repos, self.new_repos, force=force)
        # re-read self.old_repos so we can do several syncs:
        self.old_repos = self.get_old_repos(warn_if_missing_group=False)
        # if everything went well, save the manifests configurations:
        self.dump_manifest_config()
        return res

    def configure_projects(self, projects=None):
        """ Configure the given projects so that the actual git config matches
        the one coming from the manifest :

        Configure default remotes, default branches and code review, then save config
        To be called _after_ sync()
        """
        if projects is None:
            projects = self.git_worktree.get_git_projects()
        if not projects:
            return
        to_configure = list()
        srcs = {project.src: project for project in projects}
        for repo in self.new_repos:
            if repo.src in srcs.keys():
                to_configure.append(repo)
        if not to_configure:
            return
        ui.info(ui.green, ":: Setup git projects ...")
        max_src = max(len(x.src) for x in to_configure)
        n = len(to_configure)
        for i, repo in enumerate(to_configure):
            ui.info_count(i, n, ui.white, "Setup", ui.reset,
                          ui.blue, repo.src.ljust(max_src), end="\r")
            git_project = srcs[repo.src]
            git_project.apply_config()
        ui.info(" " * (max_src + 19), end="\r")
        self.git_worktree.save_git_config()

    def read_manifest_config(self):
        tree = qisys.qixml.read(self.manifest_xml)
        root = tree.getroot()
        manifest_elem = root.find("manifest")
        if manifest_elem is None:
            return
        self.manifest.url = manifest_elem.get("url")
        self.manifest.branch = manifest_elem.get("branch", "master")
        if manifest_elem.get("groups") is None:
            self.manifest.groups = None
        else:
            self.manifest.groups = qisys.qixml.parse_list_attr(manifest_elem, "groups")
        self.manifest.review = qisys.qixml.parse_bool_attr(manifest_elem, "review",
                                                           default=True)
        self.manifest.all_repos = qisys.qixml.parse_bool_attr(manifest_elem, "all_repos",
                                                              default=False)

    def dump_manifest_config(self):
        """ Save the manifest config in .qi/manifest.xml """
        root = etree.Element("worktree")
        manifest_elem = etree.SubElement(root, "manifest")
        manifest_elem.set("url", self.manifest.url)
        manifest_elem.set("branch", self.manifest.branch)
        if self.manifest.groups is not None:
            manifest_elem.set("groups", " ".join(self.manifest.groups))
        if self.manifest.review:
            manifest_elem.set("review", "true")
        else:
            manifest_elem.set("review", "false")
        tree = etree.ElementTree(root)
        qisys.qixml.write(tree, self.manifest_xml)

    def configure_manifest(self, url, branch="master", groups=None, all_repos=False,
                           ref=None, review=None, force=False):
        """ Add a manifest to the list. Will be stored in
        .qi/manifests/<name>

        """
        if review is None:
            # not set explicitely by the user,
            # (i.e not from qisrc init --no-review)
            # read it from the config
            review = self.manifest.review
        self.old_repos = self.get_old_repos(warn_if_missing_group=False)
        self.manifest.url = url
        self.manifest.groups = groups
        self.manifest.branch = branch
        self.manifest.ref = ref
        self.manifest.review = review
        self.manifest.all_repos = all_repos
        res = self.sync_repos(force=force)
        self.configure_projects()
        self.dump_manifest_config()
        return res

    def _read_import_manifest(self, parent_manifest):
        """ Read and parse imported manifest in parent_manifest recursively """
        # git clone imported manifest repository if any
        # parse all imported manifest and repo in it to parent repo list
        for import_manifest in parent_manifest.import_manifest:
            self._import_manifest(import_manifest)
            manifest_xml = os.path.join(import_manifest.repo, "manifest.xml")
            import_manifest = qisrc.manifest.Manifest(manifest_xml,
                                                      review=None)
            self._read_import_manifest(import_manifest)
            parent_manifest.repos += import_manifest.repos
            parent_manifest.groups.groups.update(import_manifest.groups.groups)

    def read_remote_manifest(self, manifest_xml=None, warn_if_missing_group=True):
        """ Read the manifest file in .qi/manifests/<name>/manifest.xml
        using the settings in .qi/manifest.xml (to know the name and the groups
        to use)
        """
        if not manifest_xml:
            manifest_xml = os.path.join(self.manifest_repo, "manifest.xml")
        remote_manifest = qisrc.manifest.Manifest(manifest_xml, review=self.manifest.review)

        # parse imported manifest recursively if any
        self._read_import_manifest(remote_manifest)

        groups = self.manifest.groups
        # if self.manifest.groups is empty but there is a default
        # group in the manifest, we need to set self.manifest.groups
        # so that subsequent calls to qisrc add-group, remove-group
        # work
        if self.manifest.groups is None:
            default_group = remote_manifest.groups.default_group
            if default_group:
                self.manifest.groups = [default_group.name]
        # Maybe some groups were removed from the manifest.
        # Only consider those which exist
        if groups is None:
            groups_to_use = None
        else:
            groups_to_use = list()
            for group in groups:
                if group in remote_manifest.groups.group_names:
                    groups_to_use.append(group)
                else:
                    if warn_if_missing_group:
                        ui.warning("Group %s not found in the manifest" % group)
        repos = remote_manifest.get_repos(groups=groups_to_use)
        return repos

    def get_old_repos(self, warn_if_missing_group=True):
        """ Backup all repos configuration before any synchronisation
        for compute_repo_diff to have the correct value

        """
        old_repos = list()
        old_repos_expected = self.read_remote_manifest(
            warn_if_missing_group=warn_if_missing_group)
        # The git projects may not match the previous repo config,
        # for instance the user removed a project by accident, or
        # a rename failed, or the project has not been cloned yet,
        # so make sure old_repos matches the worktree state:
        for old_repo in old_repos_expected:
            old_project = self.git_worktree.find_repo(old_repo)
            if old_project:
                old_repo.src = old_project.src
                old_repos.append(old_repo)
        return old_repos

    def _import_manifest(self, import_manifest=None):
        if import_manifest.project is None:
            return
        repo_name = os.path.split(import_manifest.project)[1].replace(".git", "")
        repo = os.path.join(self.git_worktree.root, ".qi", "manifests", repo_name)
        import_manifest.repo = repo
        if not os.path.exists(repo):
            qisys.sh.mkdir(repo, recursive=True)
            git = qisrc.git.Git(repo)
            git.init()
            manifest_xml = os.path.join(repo, "manifest.xml")
            with open(manifest_xml, "w") as fp:
                fp.write("<manifest />")
            git.add(".")
            git.commit("-m", "initial commit")
        if import_manifest.branch:
            import_manifest.default_branch = import_manifest.branch
        else:
            import_manifest.default_branch = self.manifest.branch
        self._sync_git(repo, import_manifest.remotes[0].url, import_manifest.default_branch, import_manifest.fixed_ref)

    def _sync_manifest(self):
        """ Update the local manifest clone with the remote """
        if not self.manifest.url:
            mess = """ \
No manifest set for worktree in {root}
Please run `qisrc init MANIFEST_URL`
"""
            raise Exception(mess.format(root=self.git_worktree.root))
        self._sync_git(self.manifest_repo, self.manifest.url, self.manifest.branch, self.manifest.ref)

    @staticmethod
    def _sync_git(repo, url, branch, ref):
        git = qisrc.git.Git(repo)
        git.set_remote("origin", url)
        if git.get_current_branch() != branch:
            git.checkout("-B", branch)
        with git.transaction() as transaction:
            git.fetch("origin")
            if ref:
                to_reset = ref
                git.reset("--hard", to_reset)
            else:
                git.reset("--hard", "origin/%s" % branch)
        if not transaction.ok:
            raise Exception("Update failed\n" + transaction.output)

    def _sync_repos(self, old_repos, new_repos, force=False):  # pylint: disable=too-many-branches
        """ Sync the remote repo configurations with the git worktree """
        res = True
        ##
        # 1/ create, remove or move the git projects:

        # Compute the work that needs to be done:
        (to_add, to_move, to_rm, to_update) = \
            compute_repo_diff(old_repos, new_repos)

        if to_rm or to_add or to_move or to_update:
            ui.info(ui.green, ":: Computing diff ...")

        if to_rm:
            for repo in to_rm:
                ui.info(ui.red, "* ", ui.reset, "removing", ui.blue, repo.src)
        if to_add:
            for repo in to_add:
                ui.info(ui.green, "* ", ui.reset, "adding", ui.blue, repo.src)

        if to_move:
            for (repo, new_src) in to_move:
                ui.info(ui.brown, "* ", ui.reset, "moving", ui.blue, repo.src,
                        ui.reset, " to ", ui.blue, new_src)

        if to_update:
            for (old_repo, new_repo) in to_update:
                ui.info(ui.green, "* ",
                        ui.reset, "updating", ui.blue, old_repo.src)
                if new_repo.review and not old_repo.review:
                    ui.info(ui.tabs(2), ui.green, "(now using code review)")
                project = self.git_worktree.get_git_project(new_repo.src)
                project.read_remote_config(new_repo)
                project.save_config()

        for repo in to_rm:
            self.git_worktree.remove_repo(repo)

        if to_add:
            ui.info(ui.green, ":: Cloning new repositories ...")

        for i, repo in enumerate(to_add):
            ui.info_count(i, len(to_add),
                          ui.blue, repo.project,
                          ui.green, "->",
                          ui.blue, repo.src,
                          ui.white, "(%s)" % repo.default_branch)
            project = self.git_worktree.get_git_project(repo.src)
            if project:  # Repo is already there, re-apply config
                project.read_remote_config(repo)
                project.save_config()
                continue
            if not self.git_worktree.clone_missing(repo):
                res = False
            else:
                project = self.git_worktree.get_git_project(repo.src)
                project.read_remote_config(repo)
                project.save_config()

        if to_move:
            ui.info(ui.green, ":: Moving repositories ...")
        for (repo, new_src) in to_move:
            if self.git_worktree.move_repo(repo, new_src, force=force):
                project = self.git_worktree.get_git_project(new_src)
                project.read_remote_config(repo)
                project.save_config()
            else:
                res = False

        return res

    def sync_from_manifest_file(self, xml_path):
        """ Just synchronize the manifest coming from one xml file.
        Used by ``qisrc check-manifest``

        """
        # don't use self.old_repos and self.new_repos here,
        # because we are only using one manifest
        # Read groups from the manifests
        old_repos = self.read_remote_manifest(warn_if_missing_group=False)
        new_repos = self.read_remote_manifest(manifest_xml=xml_path)
        return self._sync_repos(old_repos, new_repos)

    def __repr__(self):
        return "<WorkTreeSyncer in %s>" % self.git_worktree.root


class LocalManifest(object):
    """ Settings for a local manifest


    """

    def __init__(self):
        self.url = None
        self.branch = "master"
        self._groups = None
        self.ref = None  # used for snaphots or in case you
        # don't want the head of a branch
        self.review = True
        self.all_repos = False

    @property
    def groups(self):
        return self._groups

    @groups.setter
    def groups(self, groups):
        if groups is None:
            self._groups = None
        else:
            self._groups = sorted(groups)

    def __eq__(self, other):
        if not isinstance(other, LocalManifest):
            return False
        return self.url == other.url and \
            self.groups == other.groups and \
            self.ref == other.ref and \
            self.branch == other.branch and \
            self.all_repos == other.all_repos


###
# Compute updates


def compute_repo_diff(old_repos, new_repos):  # pylint: disable=too-many-branches
    """ Compute the work that needs to be done

    :returns: a tuple (to_add, to_move, to_rm, to_update)

    """
    to_add = list()
    to_move = list()
    to_rm = list()
    to_update = list()

    for new_repo in new_repos:
        for old_repo in old_repos:
            common_url = find_common_url(old_repo, new_repo)
            if common_url:
                if new_repo.src != old_repo.src:
                    to_move.append((old_repo, new_repo.src))
                # else: nothing to do
                break
        else:
            # actually we are adding repos that
            # only changed remotes, because we did not
            # commpute to_update yet
            to_add.append(new_repo)

    for old_repo in old_repos:
        for new_repo in new_repos:
            if old_repo.src != new_repo.src:
                continue

            if new_repo.remotes != old_repo.remotes\
                    or new_repo.default_branch != old_repo.default_branch\
                    or new_repo.fixed_ref != old_repo.fixed_ref:
                to_update.append((old_repo, new_repo))

            break
        else:
            if old_repo not in [x[0] for x in to_move]:
                to_rm.append(old_repo)

    really_to_add = list()
    for repo in to_add:
        if repo.src not in [x[0].src for x in to_update]:
            really_to_add.append(repo)
    to_add = really_to_add

    # sort everything by 'src':
    for repo_list in [to_add, to_rm]:
        repo_list.sort(key=lambda x: x.src)
    for repo_list in [to_move, to_update]:
        repo_list.sort(key=lambda x: x[0].src)

    return to_add, to_move, to_rm, to_update


def find_common_url(repo_a, repo_b):
    for url_a in repo_a.urls:
        for url_b in repo_b.urls:
            if url_a == url_b:
                return url_b


def compute_profile_updates(local_profiles, remote_profiles):
    """ Compare a local set of profiles with a remote set.

    Return a list of profiles to add, and a list of profiles
    that have been updated.

    """
    # Note: no profile will ever be removed, I guess we don't care
    new = list()
    updated = list()
    for remote_profile in remote_profiles.values():
        if remote_profile.name in local_profiles:
            local_profile = local_profiles.get(remote_profile.name)
            if local_profile != remote_profile:
                updated.append(remote_profile)
        else:
            new.append(remote_profile)
    return new, updated
