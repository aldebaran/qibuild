## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Handling synchronization of a worktree with a manifest

"""

from qisys import ui
import os
import qisys.qixml
import qisrc.git
import qisrc.manifest

class ManifestsWorkTree(object):
    """ Handle the manifests of a worktree

    Stores the git url of the manifests and the groups that
    should be used

    """
    def __init__(self, git_worktree):
        self.git_worktree = git_worktree
        self.manifests = dict()
        self.load_manifests()


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

    def load_manifests(self):
        """ Load every manifest, merge the results into

        """
        root = qisys.qixml.read(self.manifests_xml).getroot()
        parser = ManifestsWorkTreeParser(self)
        parser.parse(root)
        manifests = self.manifests.values()
        if not manifests:
            return
        ui.info(ui.green, "Update manifests ...")
        for manifest in self.manifests.values():
            self._update_manifest(manifest)
        self.sync_manifests()

    def dump_manifests(self):
        """ Save the manifests in .qi/manifests.xml """
        parser = ManifestsWorkTreeParser(self)
        xml = parser.xml_elem()
        qisys.qixml.write(xml, self.manifests_xml)


    def add_manifest(self, name, url, groups=None, branch="master"):
        """ Add a manifest to the list. Will be stored in
        .qi/manifests/<name>

        """
        to_add = LocalManifestSettings()
        to_add.name = name
        to_add.url = url
        to_add.groups = groups
        self.clone_manifest(name, url)
        self.manifests[name] = to_add
        self.dump_manifests()
        self.load_manifests()


    def _update_manifest(self, manifest):
        """ Update the local manifest clone with the remote """
        ui.info(ui.green, " * ",
                ui.reset, ui.blue, manifest.name,
                ui.reset, ui.bold, "(%s)" % manifest.branch)
        manifest_repo = os.path.join(self.manifests_root, manifest.name)
        git = qisrc.git.Git(manifest_repo)
        with git.transaction() as transaction:
            git.fetch("origin")
            git.checkout("-B", manifest.branch)
            git.reset("--hard", "origin/%s" % manifest.branch)
        if not transaction.ok:
            ui.warning("Update failed")
            ui.info(transaction.output)

    def sync_manifests(self):
        """ Sync the git worktree with every manifest """
        for manifest in self.manifests.values():
            self.sync_manifest(manifest)

    def sync_manifest(self, local_manifest):
        """ Sync the remote repo configurations with the git worktree """
        ui.info(ui.green, "Syncing", local_manifest.name, "...")
        manifest_xml = os.path.join(self.manifests_root, local_manifest.name,
                                    "manifest.xml")
        remote_manifest = qisrc.manifest.Manifest(manifest_xml)
        groups = local_manifest.groups
        repos = remote_manifest.get_repos(groups=groups)
        for i, repo in enumerate(repos, start=1):
            ui.info(ui.green, " * ",
                    ui.reset, ui.bold, "(%d / %d)" % (i, len(repos)),
                    ui.reset, ui.bold, repo.src)

            self.sync_manifest_repo(repo)

    def sync_manifest_repo(self, repo):
        """ Sync one remote configuration with the git worktree """
        project_url = repo.remote_url
        git_project = self.git_worktree.find_url(project_url)
        if not git_project:
            self.git_worktree.clone_missing(repo)
            return
        if git_project.src == repo.src:
            git_project.sync(repo)
        else:
            # Project has moved:
            self.git_worktree.move_repo(git_project, repo.src)

    def clone_manifest(self, name, url, branch="master"):
        """ Clone a new manifest in .qi/manifests/<name>

        """
        manifest_repo = os.path.join(self.manifests_root, name)
        git = qisrc.git.Git(manifest_repo)
        git.clone(url, "--branch", branch)



class LocalManifestSettings(object):
    """ Settings for a local manifests """
    def __init__(self):
        self.name = None
        self.url = None
        self.branch = "master"
        self.groups = list()


##
# Parsing

class ManifestsWorkTreeParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ManifestsWorkTreeParser, self).__init__(target)
        self._ignore = ["manifests_xml", "manifests_root"]

    def _parse_manifest(self, elem):
        manifest_settings = LocalManifestSettings()
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

