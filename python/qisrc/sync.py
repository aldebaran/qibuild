## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with some manifests

"""

import os

from qisys import ui
import qisys.qixml
import qisrc.git
import qisrc.manifest
import qibuild.profile


class WorkTreeSyncer(object):
    """ Handle the manifests of a worktree

    Stores the git url of the manifests and the groups that
    should be used, synchronizes the local manifests with the git
    worktree

    """
    def __init__(self, git_worktree):
        self.git_worktree = git_worktree
        # Read manifest configuration now, before any
        # new manifest is cloned or updated
        self.manifests = dict()
        root = qisys.qixml.read(self.manifests_xml).getroot()
        parser = WorkTreeSyncerParser(self)
        parser.parse(root)
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

    def sync_repos(self):
        """ Update every manifest, inspect changes, and updates the
        git worktree accordingly

        """
        res = True
        manifests = self.manifests.values()
        if not manifests:
            return
        ui.info(ui.green, ":: Updating manifests ...")
        for local_manifest in self.manifests.values():
            ui.info(ui.green, "* ",
                    ui.reset, ui.blue, local_manifest.name,
                    ui.reset, ui.bold, "(%s)" % local_manifest.branch,
                    end="")
            if local_manifest.groups:
                ui.info("groups", ", ".join(local_manifest.groups))
            else:
                ui.info()
            self._sync_manifest(local_manifest)
            self._sync_build_profiles(local_manifest)
            self._sync_groups(local_manifest)
        self.new_repos = self.get_new_repos()
        res = self._sync_repos(self.old_repos, self.new_repos)
        # re-read self.old_repos so we can do several syncs:
        self.old_repos = self.get_old_repos()
        # if everything went well, save the manifests configurations:
        self.dump_manifests()
        return res

    def dump_manifests(self):
        """ Save the manifests in .qi/manifests.xml """
        parser = WorkTreeSyncerParser(self)
        xml = parser.xml_elem()
        qisys.qixml.write(xml, self.manifests_xml)

    def configure_manifest(self, name, url, groups=None, branch="master"):
        """ Add a manifest to the list. Will be stored in
        .qi/manifests/<name>

        """
        self.old_repos = self.get_old_repos()
        to_add = LocalManifest()
        to_add.name = name
        to_add.url = url
        to_add.groups = groups
        to_add.branch = branch
        self.manifests[name] = to_add
        self.clone_manifest(to_add)
        self.sync_repos()

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
                old_project = self.git_worktree.find_repo(old_repo)
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
                if new_repo.review:
                    ui.info(ui.tabs(2), ui.green, "(now using code review)")


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
            if self.git_worktree.get_git_project(repo.src):
                continue
            if not self.git_worktree.clone_missing(repo):
                res = False

        if to_move:
            ui.info(ui.green, ":: Moving repositories ...")
        for (repo, new_src) in to_move:
            if not self.git_worktree.move_repo(repo, new_src):
                res = False

        ##
        # 2/ Apply configuration to every new repositories
        todo = list() # a list of tuples (project, repo)
        for repo in new_repos:
            git_project = self.git_worktree.get_git_project(repo.src)
            # may not work if the moving failed for instance
            if git_project:
                todo.append((git_project, repo))

        if not todo:
            return

        ui.info(ui.green, ":: Configuring projects ...")
        max_src = max([len(x[0].src) for x in todo])
        n = len(todo)
        for i, (project, repo) in enumerate(todo):
            ui.info_count(i, n, ui.white, "Configuring", ui.reset,
                          ui.blue, project.src.ljust(max_src), end="\r")
            project.apply_remote_config(repo)
        ui.info(" " * (max_src + 19), end="\r")
        return res

    def _sync_build_profiles(self, local_manifest):
        """ Synchronize the build profiles read from the given manifest """
        local_xml = os.path.join(self.git_worktree.root, ".qi", "qibuild.xml")
        if not os.path.exists(local_xml):
            with open(local_xml, "w") as fp:
                fp.write("<qibuild />")
        remote_xml = os.path.join(self.manifests_root,
                                  local_manifest.name, "manifest.xml")
        local = qibuild.profile.parse_profiles(local_xml)
        remote = qibuild.profile.parse_profiles(remote_xml)
        new_profiles, updated_profiles = compute_profile_updates(local, remote)
        if new_profiles or updated_profiles:
            ui.info(ui.green, ":: Synchronizing build profiles ...")
        for new_profile in new_profiles:
            ui.info(ui.green, " * New:", ui.blue, new_profile.name)
            qibuild.profile.configure_build_profile(local_xml,
                                                    new_profile.name,
                                                    new_profile.cmake_flags)
        if updated_profiles:
            mess = "The following profiles have been updated remotely:\n"
            for updated_profile in updated_profiles:
                mess += "  * " + updated_profile.name + "\n"
            ui.warning(mess)

    def _sync_groups(self, local_manifest):
        """ Synchronize the repsitories groups read from the given manifest """
        # FIXME: what to do when there are several manifests with different
        # groups in them?
        remote_xml = os.path.join(self.manifests_root,
                                  local_manifest.name, "manifest.xml")
        remote_root_elem = qisys.qixml.read(remote_xml).getroot()
        remote_groups_elem = remote_root_elem.find("groups")
        if remote_groups_elem is None:
            remote_groups_elem = qisys.qixml.etree.Element("groups")

        groups_xml = os.path.join(self.git_worktree.root, ".qi", "groups.xml")
        qisys.qixml.write(remote_groups_elem, groups_xml)


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
        return self._sync_repos(old_repos, new_repos)


    def clone_manifest(self, manifest):
        """ Clone a new manifest in .qi/manifests/<name>

        """
        manifest_repo = os.path.join(self.manifests_root, manifest.name)
        if not os.path.exists(manifest_repo):
            git = qisrc.git.Git(manifest_repo)
            git.clone(manifest.url, "--branch", manifest.branch, quiet=True)
        else:
            ui.warning("Manifest %s already exists." % manifest.name)


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

###
# Compute updates



def compute_repo_diff(old_repos, new_repos):
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
                if new_repo.src == old_repo.src:
                    pass # nothing to do
                else:
                    to_move.append((old_repo, new_repo.src))
                break
        else:
            # actually we are adding repos that
            # only changed remotes, because we did not
            #commpute to_update yet
            to_add.append(new_repo)

    for old_repo in old_repos:
        for new_repo in new_repos:
            if old_repo.src == new_repo.src:
                if new_repo.remotes == old_repo.remotes:
                    if new_repo.default_branch == old_repo.default_branch:
                        pass
                    else:
                        to_update.append((old_repo, new_repo))
                else:
                    to_update.append((old_repo, new_repo))
                break
        else:
            if not old_repo in [x[0] for x in to_move]:
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

    return (to_add, to_move, to_rm, to_update)

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
