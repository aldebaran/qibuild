import os
import functools

from qisys import ui
import qisys.qixml
import qisrc.git_config

class GitProject(object):
    def __init__(self, git_worktree, worktree_project):
        self.git_worktree = git_worktree
        self.src = worktree_project.src
        self.name = ""
        self.branches = list()
        self.remotes = list()
        self.review = False

    def load_xml(self, xml_elem):
        parser = GitProjectParser(self)
        parser.parse(xml_elem)

    def dump_xml(self):
        parser = GitProjectParser(self)
        return parser.xml_elem(node_name="project")

    def save_config(self):
        self.apply_config()
        self.git_worktree.save_project_config(self)

    @property
    def default_branch(self):
        """ The default branch for this repository """
        for branch in self.branches:
            if branch.default:
                return branch

    @property
    def review_remote(self):
        """ The remote to use when doing code review """
        for remote in self.remotes:
            if remote.review:
                return remote

    @property
    def default_remote(self):
        """ The remote to use by default """
        for remote in self.remotes:
            if remote.default:
                return remote

    @property
    def clone_url(self):
        """ The url to use when cloning this repository for
        the first time

        """
        return self.default_remote.url

    @property
    def path(self):
        """ The full, native path to the underlying git repository """
        res = os.path.join(self.git_worktree.root, self.src)
        return qisys.sh.to_native_path(res)


    def configure_remote(self, remote):
        """ Configure a remote. If a remote with the same name
        exists, its url will be overwritten

        """
        for previous_remote in self.remotes:
            if previous_remote.name == remote.name:
                self.update_remote(previous_remote, remote)
                return
        self.remotes.append(remote)

    def update_remote(self, remote, new):
        """ Helper for configure_remote """
        if not remote.review and new.review:
            ui.info(self.src, "is now under code review")
        if remote.review and not new.review:
            ui.warning(self.src, "is no longer code review")
        if remote.url != new.url:
            ui.warning(self.src, ": remote url changed", remote.url, "->", new.url)
        self.remotes.remove(remote)
        self.remotes.append(new)

    def configure_branch(self, name, tracks="origin",
                         remote_branch=None, default=True):
        """ Configure a branch. If a branch with the same name
        already exitsts, update its tracking remote.

        """
        previous_default_branch = self.default_branch
        if previous_default_branch and previous_default_branch.name != name:
            ui.warning(self.src, ": default branch changed",
                        previous_default_branch.name, "->", name)
            previous_default_branch.default = False
        branch_found = False
        for branch in self.branches:
            if branch.name == name:
                branch_found = True
                if branch.tracks != tracks:
                    ui.warning(self.src, ":", branch.name, "now tracks", tracks,
                              "instead of", branch.tracks)
                    branch.tracks = tracks
                branch.default = default
        if not branch_found:
            branch = qisrc.git_config.Branch()
            branch.name = name
            branch.tracks = tracks
            branch.remote_branch = remote_branch
            branch.default = default
            self.branches.append(branch)
        return branch

    def apply_remote_config(self, repo):
        """ Apply the configuration read from the "repo" setting
        of a remote manifest.
        Called by WorkTreeSyncer

        """
        previous_default = None
        if self.default_remote:
            previous_default = self.default_remote.name

        self.name = repo.project
        for remote in repo.remotes:
            self.configure_remote(remote)
        self.configure_branch(repo.default_branch, tracks=repo.default_remote.name,
                              remote_branch=repo.default_branch, default=True)
        if repo.review:
            ok = qisrc.review.setup_project(self)
            if ok:
                self.review = True
        new_default = self.default_remote.name
        if previous_default is not None and previous_default != new_default:
            ui.warning("Default remote changed", previous_default, "->",
                                                 new_default)
        self.save_config()


    def sync(self, branch_name=None, rebase_devel=False,
             **kwargs):
        """ Synchronize remote changes with the underlying git repository
        Calls py:meth:`qisys.git.Git.sync`

        """
        git = qisrc.git.Git(self.path)
        if branch_name is None:
            branch = self.default_branch
            if not branch:
                return None, "No branch given, and no branch configured by default"
        else:
            branch = git.get_branch(branch_name)

        current_branch = git.get_current_branch()
        if not current_branch:
            return None, "Not on any branch"

        if current_branch != branch.name and not rebase_devel:
            return None, "Not on the correct branch. " + \
                         "On %s but should be on %s" % (current_branch, branch.name)

        return git.sync_branch(branch)


    def get_branch(self, branch_name):
        """ Get the branch matching the name
        :return: None if not found

        """
        for branch in self.branches:
            if branch.name == branch_name:
                return branch

    def apply_config(self):
        """ Apply configuration to the underlying git
        repository

        """
        git = qisrc.git.Git(self.path)
        for remote in self.remotes:
            git.set_remote(remote.name, remote.url)
        for branch in self.branches:
            git.set_tracking_branch(branch.name, branch.tracks,
                                    remote_branch=branch.remote_branch)


    def __eq__(self, other):
        return self.src == other.src

    def __ne__(self, other):
        return not self.__eq__(other)

    def __repr__(self):
        return "<GitProject in %s>" % self.src
##
# Parsing

class GitProjectParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GitProjectParser, self).__init__(target)
        self._ignore = ["worktree", "path", "clone_url",
                        "default_branch", "review_url"]
        self._required = ["src"]

    def _parse_remote(self, elem):
        remote = qisrc.git_config.Remote()
        parser = qisrc.git_config.RemoteParser(remote)
        parser.parse(elem)
        self.target.remotes.append(remote)

    def _parse_branch(self, elem):
        branch = qisrc.git_config.Branch()
        parser = qisrc.git_config.BranchParser(branch)
        parser.parse(elem)
        self.target.branches.append(branch)

    def _write_branches(self, elem):
        for branch in self.target.branches:
            parser = qisrc.git_config.BranchParser(branch)
            branch_xml = parser.xml_elem()
            elem.append(branch_xml)

    def _write_remotes(self, elem):
        for remote in self.target.remotes:
            parser = qisrc.git_config.RemoteParser(remote)
            remote_xml = parser.xml_elem()
            elem.append(remote_xml)
