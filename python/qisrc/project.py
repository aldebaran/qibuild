import os
import functools

from qisys import ui
import qisrc.git_config

class GitProject(object):
    def __init__(self, git_worktree, worktree_project):
        self.git_worktree = git_worktree
        self.src = worktree_project.src
        self.branches = list()
        self.remotes = list()
        self.review = False

    @property
    def default_branch(self):
        """ The default branch for this repository """
        for branch in self.branches:
            if branch.default:
                return branch

    @property
    def clone_url(self):
        """ The url to use when cloning this repository for
        the first time

        """
        default_branch = self.default_branch
        if not default_branch:
            return None
        tracked = default_branch.tracks
        if not tracked:
            return None
        for remote in self.remotes:
            if remote.name == tracked:
                return remote.url
        return None

    # pylint: disable-msg=E0213
    def change_config(func):
        """ Decorator for every function that changes the git configuration

        """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            # pylint: disable-msg=E1102
            res = func(self, *args, **kwargs)
            self.apply_config()
            self.git_worktree.save_project_config(self)
            return res
        return new_func

    @property
    def path(self):
        """ The full, native path to the underlying git repository """
        return os.path.join(self.git_worktree.root, self.src)


    @change_config
    def configure_remote(self, name, url=None, review=False):
        """ Configure a remote. If a remote with the same name
        exists, its url will be overwritten

        """
        remote_found = False
        for remote in self.remotes:
            if remote.name == name:
                remote_found = True
                if remote.review != review and review:
                    ui.info(self.src, "now under code review")
                remote.review = review
                if remote.url != url:
                    ui.warning(self.src, ": remote url changed", url, "->", remote.url)
                    remote.url = url
        if not remote_found:
            remote = qisrc.git_config.Remote()
            remote.name = name
            remote.url = url
            remote.review = review
            self.remotes.append(remote)

    @change_config
    def configure_branch(self, name, tracks="origin",
                         remote_branch=None, default=True):
        """ Configure a branch. If a branch with the same name
        already exitsts, update its tracking remote.

        """
        if self.default_branch and self.default_branch.name != name:
            ui.warning(self.src, ": default branch changed",
                        self.default_branch.name, "->", name)
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

    @change_config
    def apply_remote_config(self, repo):
        """ Apply the configuration read from the "repo" setting
        of a remote manifest.
        Called by WorkTreeSyncer

        """
        self.configure_branch(repo.default_branch, tracks=repo.remote,
                              remote_branch=repo.default_branch, default=True)
        self.configure_remote(repo.remote, repo.remote_url, review=repo.review)
        if repo.review:
            ok = qisrc.review.setup_project(self.path, repo.project, repo.remote_url)
            if ok:
                self.review = True
                self.git_worktree.save_project_config(self)


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


    def __repr__(self):
        return "<GitProject in %s>" % self.src
