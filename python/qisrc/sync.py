## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with some manifests

"""

from qisys import ui
import os
import qisys.qixml
import qisrc.git
import qisrc.manifest


def compute_repo_diff(old_repos, new_repos):
    """ Compute the work that needs to be done

    :returns: a tuple (to_add, to_move, to_rm)

    """
    to_add = list()
    to_move = list()
    to_rm = list()

    # Look for the moves:
    for old_repo in old_repos:
        for new_repo in new_repos:
            if old_repo.remote_url == new_repo.remote_url:
                if old_repo.src != new_repo.src:
                    to_move.append((old_repo, new_repo.src))

    old_dict = dict()
    for old_repo in old_repos:
        old_dict[old_repo.remote_url] = old_repo
    new_dict = dict()
    for new_repo in new_repos:
        new_dict[new_repo.remote_url] = new_repo

    for old_repo in old_repos:
        if not old_repo.remote_url in new_dict:
            to_rm.append(old_repo)

    for new_repo in new_repos:
        if not new_repo.remote_url in old_dict:
            to_add.append(new_repo)

    return (to_add, to_move, to_rm)

class WorkTreeSyncer(object):
    """ Handle the manifests of a worktree

    Stores the git url of the manifests and the groups that
    should be used, synchronizes the local manifests with the git
    worktree

    """
    def __init__(self, git_worktree, sync_first=True):
        self.git_worktree = git_worktree
        # Read manifest configuration now, before any
        # new manifest is cloned or updated
        self.manifests = dict()
        root = qisys.qixml.read(self.manifests_xml).getroot()
        parser = WorkTreeSyncerParser(self)
        parser.parse(root)
        self.old_repos = list()
        self.new_repos = list()
        if sync_first:
            # backup old repos configuration now, so that
            # we know what to sync
            self.old_repos = self.get_old_repos()
            self.sync_manifests()
            self.dump_manifests()

    @property
    def manifests_xml(self):
        manifests_xml_path = os.path.join(self.git_worktree.root,
                                          ".qi", "manifests.xml")
        if not os.path.exists(manifests_xml_path):
            with open(manifests_xml_path, "w") as fp:
                fp.write("<manifests />")
        return manifests_xml_path

    @property
    def manifests_root(self):
        res = os.path.join(self.git_worktree.root, ".qi", "manifests")
        qisys.sh.mkdir(res)
        return res

    def sync_manifests(self):
        """ Update every manifest, inspect changes, and updates the
        git worktree accordingly

        """
        manifests = self.manifests.values()
        if not manifests:
            return
        ui.info(ui.green, "Update manifests ...")
        for i, local_manifest in enumerate(self.manifests.values()):
            ui.info_count(i, len(self.manifests),
                          ui.reset, ui.blue, local_manifest.name,
                          ui.reset, ui.bold, "(%s)" % local_manifest.branch)
            if local_manifest.groups:
                ui.info(ui.bold, ui.tabs(2), "Using groups:",
                        ui.reset, ui.green, ", ".join(local_manifest.groups))
            self._sync_manifest(local_manifest)
        self.new_repos = self.get_new_repos()
        self._sync_repos(self.old_repos, self.new_repos)
        # re-read self.old_repos so we can do several syncs:
        self.old_repos = self.get_old_repos()

    def dump_manifests(self):
        """ Save the manifests in .qi/manifests.xml """
        parser = WorkTreeSyncerParser(self)
        xml = parser.xml_elem()
        qisys.qixml.write(xml, self.manifests_xml)


    def configure_manifest(self, name, url, groups=None, branch="master"):
        """ Add a manifest to the list. Will be stored in
        .qi/manifests/<name>

        """
        # Backup before sync in case sync_first was not used
        self.old_repos = self.get_old_repos()
        to_add = LocalManifest()
        to_add.name = name
        to_add.url = url
        to_add.groups = groups
        to_add.branch = branch
        self.manifests[name] = to_add
        self.clone_manifest(to_add)
        self.sync_manifests()
        self.dump_manifests()

    def remove_manifest(self, name):
        """ Remove a manifest from the list """
        if not name in self.manifests:
            raise Exception("No such manifest: %s", name)
        del self.manifests[name]
        to_rm = os.path.join(self.manifests_root, name)
        qisys.sh.rm(to_rm)
        self.dump_manifests()

    def read_remote_manifest(self, local_manifest, manifest_xml=None):
        """ Read the manifest file in .qi/manifests/<name>/manifest.xml
        using the settings in .qi/manifest.xml (to know the name and the groups
        to use)
        """
        if not manifest_xml:
            manifest_xml = os.path.join(self.manifests_root,
                                        local_manifest.name, "manifest.xml")
        remote_manifest = qisrc.manifest.Manifest(manifest_xml)
        groups = local_manifest.groups
        repos = remote_manifest.get_repos(groups=groups)
        return repos

    def get_old_repos(self):
        """ Backup all repos configuration before any synchronisation
        for compute_repo_diff to have the correct value

        """
        old_repos = list()
        for manifest in self.manifests.values():

            old_repos_expected = self.read_remote_manifest(manifest)
            # The git projects may not match the previous repo config,
            # for instance the user removed a project by accident, or
            # a rename failed, or the project has not been cloned yet,
            # so make sure old_repos matches the worktree state:
            for old_repo in old_repos_expected:
                old_project = self.git_worktree.find_url(old_repo.remote_url)
                if old_project:
                    old_repo.src = old_project.src
                    old_repos.append(old_repo)
        return old_repos

    def get_new_repos(self):
        """ Read all the repos coming from all the manifests

        """
        all_new_repos = list()
        for manifest in self.manifests.values():
            new_repos = self.read_remote_manifest(manifest)
            all_new_repos.extend(new_repos)
        return all_new_repos


    def _sync_manifest(self, local_manifest):
        """ Update the local manifest clone with the remote """
        manifest_repo = os.path.join(self.manifests_root, local_manifest.name)
        git = qisrc.git.Git(manifest_repo)
        with git.transaction() as transaction:
            git.fetch("origin")
            git.checkout("-B", local_manifest.branch)
            git.reset("--hard", "origin/%s" % local_manifest.branch)
        if not transaction.ok:
            ui.warning("Update failed")
            ui.info(transaction.output)
            return


    def _sync_repos(self, old_repos, new_repos):
        """ Sync the remote repo configurations with the git worktree """
        # Compute the work that needs to be done:
        (to_add, to_move, to_rm) = \
            compute_repo_diff(old_repos, new_repos)

        if to_add:
            ui.info(ui.tabs(2), ui.green , "To add:")
            for repo in to_add:
                ui.info(ui.tabs(3),
                        ui.green, "* ", ui.reset, ui.blue, repo.src)

        if to_rm:
            ui.info(ui.tabs(2), "To remove:")
            for repo in to_add:
                ui.info(ui.tabs(3),
                        ui.red, "* ", ui.reset, ui.blue, repo.src)

        if to_move:
            ui.info(ui.tabs(2), ui.brown, "To move:")
            for (repo, new_src) in to_move:
                ui.info(ui.tabs(3),
                        ui.brown, "* ", ui.reset, ui.blue, repo.src,
                        ui.reset, " -> ", ui.blue, new_src)

        for repo in to_add:
            # maybe user created it already, for instance with
            # a sucessful `qisrc sync`
            if not self.git_worktree.get_git_project(repo.src):
                self.git_worktree.clone_missing(repo)

        for (repo, new_src) in to_move:
            self.git_worktree.move_repo(repo, new_src)

        for repo in to_rm:
            self.git_worktree.remove_repo(repo)

        for repo in new_repos:
            git_project = self.git_worktree.get_git_project(repo.src)
            # may not work if the moving failed for instance
            if git_project:
                git_project.sync(repo)

    def sync_manifest_repo(self, repo):
        """ Sync one remote configuration with the git worktree """
        project_url = repo.remote_url
        git_project = self.git_worktree.find_url(project_url)
        if not git_project:
            return
        if git_project.src != repo.src:
            # Project has moved:
            self.git_worktree.move_repo(git_project, repo.src)
        git_project.sync(repo)

    def sync_from_manifest_file(self, name, xml_path):
        """ Just synchronize the manifest coming from one xml file.
        Used by ``qisrc manifest --check``

        """
        # don't use self.old_repos and self.new_repos here,
        # because we are only using one manifest
        # Read groups from the manifests
        local_manifest = self.manifests[name]
        old_repos = self.read_remote_manifest(local_manifest)
        new_repos = self.read_remote_manifest(local_manifest,
                                              manifest_xml=xml_path)
        self._sync_repos(old_repos, new_repos)


    def clone_manifest(self, manifest):
        """ Clone a new manifest in .qi/manifests/<name>

        """
        manifest_repo = os.path.join(self.manifests_root, manifest.name)
        if not os.path.exists(manifest_repo):
            git = qisrc.git.Git(manifest_repo)
            git.clone(manifest.url, "--branch", manifest.branch, quiet=True)

    def __repr__(self):
        return "<WorkTreeSyncer in %s>" % self.git_worktree.root


class LocalManifest(object):
    """ Settings for a local manifest


    """
    def __init__(self):
        self.name = None
        self.url = None
        self.branch = "master"
        self.groups = list()


##
# Parsing

class WorkTreeSyncerParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(WorkTreeSyncerParser, self).__init__(target)
        self._ignore = ["manifests_xml", "manifests_root",
                        "old_repos", "new_repos"]

    def _parse_manifest(self, elem):
        manifest_settings = LocalManifest()
        parser = LocalManifestParser(manifest_settings)
        parser.parse(elem)
        self.target.manifests[manifest_settings.name] = manifest_settings

    def _write_manifests(self, elem):
        for name in self.target.manifests:
            parser = LocalManifestParser(self.target.manifests[name])
            manifest_elem = parser.xml_elem(node_name="manifest")
            elem.append(manifest_elem)

class LocalManifestParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(LocalManifestParser, self).__init__(target)
        self._required = ["name"]

