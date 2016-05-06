## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import copy
import functools

from qisys import ui
import qisys.qixml
import qisrc.git_config

@functools.total_ordering
class GitProject(object):
    def __init__(self, git_worktree, worktree_project):
        self.git_worktree = git_worktree
        self.src = worktree_project.src
        self.worktree_project = worktree_project
        self.name = ""
        self.branches = list()
        self.remotes = list()
        self.review = False
        self.fixed_ref = None

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
    def qiproject_xml(self):
        """ Path to qiproject.xml. Used by qisrc push to find
        the list of maintainers

        """
        return self.worktree_project.qiproject_xml

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
        if self.default_remote is None:
            return None
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
        if remote == new:
            return  # Be lazy
        if not remote.review and new.review:
            ui.info(self.src, "is now under code review")
        if remote.review and not new.review:
            ui.warning(self.src, "is no longer under code review")
        if remote.url != new.url:
            ui.warning(self.src, ": remote url changed", remote.url, "->", new.url)
        self.remotes.remove(remote)
        self.remotes.append(new)

    def configure_branch(self, name, tracks="origin",
                         remote_branch=None, default=True,
                         quiet=False):
        """ Configure a branch. If a branch with the same name
        already exists, update its tracking remote.

        """
        previous_default_branch = self.default_branch
        if previous_default_branch and previous_default_branch.name != name:
            if not quiet:
                ui.warning(self.src, ": default branch changed",
                            previous_default_branch.name, "->", name)
            previous_default_branch.default = False
        branch_found = False
        for branch in self.branches:
            if branch.name == name:
                branch_found = True
                if branch.tracks != tracks:
                    if not quiet:
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

    def read_remote_config(self, repo, quiet=False):
        """ Apply the configuration read from the "repo" setting
        of a remote manifest.
        Called by WorkTreeSyncer

        """
        previous_default = None
        if self.default_remote:
            previous_default = self.default_remote.name

        self.name = repo.project
        self.remotes = list()
        for remote in repo.remotes:
            self.configure_remote(remote)
        if repo.default_branch and repo.default_remote:
            self.configure_branch(repo.default_branch, tracks=repo.default_remote.name,
                                  remote_branch=repo.default_branch, default=True,
                                  quiet=quiet)
            new_default = self.default_remote.name
            if previous_default is not None and previous_default != new_default:
                if not quiet:
                    ui.warning("Default remote changed", previous_default, "->",
                                                        new_default)
        if repo.review and not self.review:
        # Project is now under code review, try to setup
        # gerrit and save success in self.review
        # (so that we can retry if gerrit setup did not work)
            ok = qisrc.review.setup_project(self)
            if ok:
                self.review = True
            else:
                self.review = False
        if not repo.review and self.review:
            # Project was under code review, but no longer is,
            # simply set self.review to False so that `qisrc push`
            # does not try to push to gerrit
            self.review = False
        if repo.fixed_ref:
            if not self.fixed_ref:
                ui.warning("Now using fixed ref:", repo.fixed_ref)
            self.fixed_ref = repo.fixed_ref

    def to_repo(self):
        """ The opposite of read_remote_config(). Return a RepoConfig object
        from the settings found in .qi/git.xml

        """
        res = qisrc.manifest.RepoConfig()
        res.src = self.src
        res.project = self.name
        if self.default_branch:
            res.default_branch = self.default_branch.name
        res.fixed_ref = self.fixed_ref
        res.remotes = self.remotes
        return res

    def sync(self, rebase_devel=False, **kwargs):
        """ Synchronize remote changes with the underlying git repository
        Calls :py:meth:`qisrc.git.Git.sync_branch`

        .. warning::
           this method is called in parallel when calling ``qisrc sync``,
           therefore it must not cause any side-effect on the global state
           outside of this repo.
        """
        git = qisrc.git.Git(self.path)
        branch = self.default_branch
        if not branch:
            return None, "No branch given, and no branch configured by default"

        rc, out = git.fetch(raises=False)
        if rc != 0:
            return False, "fetch failed\n" + out

        if self.fixed_ref:
            return self.safe_reset_ref(self.fixed_ref)

        current_branch = git.get_current_branch()
        if not current_branch:
            return None, "Not on any branch"

        if current_branch != branch.name and not rebase_devel:
            return None, "Not on the correct branch. " + \
                         "On %s but should be on %s" % (current_branch, branch.name)

        if current_branch != branch.name and rebase_devel:
            return git.sync_branch_devel(branch, fetch_first=False)

        # Here current_branch == branch.name
        return git.sync_branch(branch, fetch_first=False)

    def safe_reset_ref(self, ref):
        """ Read a fixed ref from the remote config.
        Make sure to not discard any local changes

        """
        git = qisrc.git.Git(self.path)
        ok, mess = git.require_clean_worktree()
        if not ok:
            return None, "Skipped: " + mess
        ok, mess = qisrc.reset.clever_reset_ref(self, ref, raises=False)
        return ok, mess

    def reset(self):
        """ Same as sync, but discard any local changes

        .. warning::
           this method is called in parallel when calling ``qisrc sync``,
           therefore it must not cause any side-effect on the global state
           outside of this repo.
        """
        git = qisrc.git.Git(self.path)
        branch = self.default_branch
        if not branch:
            return None, "No branch given, and no branch configured by default"

        rc, out = git.fetch(raises=False)
        if rc != 0:
            return False, "fetch failed\n" + out

        rc, out = git.checkout("-B", branch.name, raises=False)
        if rc != 0:
            return False, "checkout failed\n" + out

        remote_branch = branch.remote_branch
        if not remote_branch:
            remote_branch = branch.name
        remote_ref = "%s/%s" % (branch.tracks, remote_branch)
        rc, out = git.reset("--hard", remote_ref, raises=False)
        if rc != 0:
            return False, "reset --hard failed\n" + out

        return True, "reset to %s\n" % remote_ref + out

    def apply_config(self):
        """ Apply configuration to the underlying git
        repository

        """
        git = qisrc.git.Git(self.path)
        if git.is_empty():
            ui.error("repo in %s has no commits yet" % self.src)
        for remote in self.remotes:
            git.set_remote(remote.name, remote.url)
        for branch in self.branches:
            if branch.tracks:
                git.set_tracking_branch(branch.name, branch.tracks,
                                        remote_branch=branch.remote_branch)

    def __deepcopy__(self, memo):
        shallow_copy = copy.copy(self)
        shallow_copy.branches = copy.deepcopy(self.branches)
        shallow_copy.remotes = copy.deepcopy(self.remotes)
        return shallow_copy

    def __eq__(self, other):
        return self.src == other.src

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.src)

    def __lt__(self, other):
        return self.src < other.src

    def __repr__(self):
        return "<GitProject in %s>" % self.src
##
# Parsing

class GitProjectParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GitProjectParser, self).__init__(target)
        self._ignore = ["worktree", "path", "clone_url",
                        "default_branch", "review_url",
                        "qiproject_xml"]
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
