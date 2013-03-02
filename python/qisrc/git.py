## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.

## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" A Pythonic git API

"""
import os
import contextlib
import subprocess
import functools

from qisys import ui
import qisys
import qisys.command

class Git(object):
    """ The Git represent a git tree """
    def __init__(self, repo):
        """ :param repo: The path to the tree """
        self.repo = repo
        self._transaction = None

    def call(self, *args, **kwargs):
        """
        Call a git command

        :param args: The arguments of the command.
                     For instance ["frobnicate", "--spam=eggs"]

        :param kwargs: Will be passed to subprocess.check_call()
                       command, with the following changes:

           * if cwd is not given it will be self.repo instead
           * if env is not given it will be read from the config file
           * if raises is False, no exception will be raised if command
             fails, and a (retcode, output) tuple will be returned.
        """
        if not self._transaction:
            return self._call(*args, **kwargs)

        if not self._transaction.ok:
            # Do not run any more  command if transaction failed:
            return

        # Force raises to False
        kwargs["raises"] = False
        (retcode, out) = self._call(*args, **kwargs)
        if retcode != 0:
            self._transaction.ok = False
            self._transaction.output += "git %s failed\n" % (" ".join(args))
            self._transaction.output += out


    def _call(self, *args, **kwargs):
        """ Helper for self.call """
        ui.debug("git", " ".join(args))
        if not "cwd" in kwargs.keys():
            kwargs["cwd"] = self.repo
        if not "quiet" in kwargs.keys():
            kwargs["quiet"] = False
        git = qisys.command.find_program("git", raises=True)
        cmd = [git]
        cmd.extend(args)
        raises = kwargs.get("raises")
        if raises is False:
            del kwargs["raises"]
            del kwargs["quiet"]
            process = subprocess.Popen(cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                **kwargs)
            out = process.communicate()[0]
            # Don't want useless blank lines
            out = out.rstrip("\n")
            ui.debug("out:", out)
            return (process.returncode, out)
        else:
            qisys.command.call(cmd, **kwargs)

    @contextlib.contextmanager
    def transaction(self):
        """ Start a series of git commands """
        self._transaction = Transaction()
        yield self._transaction
        self._transaction = None


    def get_config(self, name):
        """ Get a git config value.
        Return None if not found

        """
        (status, out) = self.config("--get", name, raises=False)
        if status != 0:
            return None
        return out.strip()

    def set_config(self, name, value):
        """ Set a new config value.
        Will be created if it does not exist
        """
        self.config(name, value)

    def get_current_ref(self, ref="HEAD"):
        """ return the current ref
        git symbolic-ref HEAD
        else: git name-rev --name-only --always HEAD
        """
        (status, out) = self.call("symbolic-ref", ref, raises=False)
        lines = out.splitlines()
        if len(lines) < 1:
            return None
        if status != 0:
            return None
        return lines[0]

    def get_current_branch(self):
        """ return the current branch """
        branch = self.get_current_ref()
        if not branch:
            return branch
        return branch[11:]


    def get_tracking_branch(self, branch=None):
        if not branch:
            branch = self.get_current_branch()

        remote = self.get_config("branch.%s.remote" % branch)
        merge  = self.get_config("branch.%s.merge" % branch)
        if not remote:
            return None
        if not merge:
            return None
        if merge.startswith("refs/heads/"):
            return "%s/%s" % (remote, merge[11:])
        return "%s/%s" % (remote, merge)

    def __getattr__(self, name):
        """Generate generic wrapper for call."""
        # If you want to specialize one, remove it from whitelist and write it
        # by hand (see clone).
        # Only porcelain here.
        whitelist = ("add", "branch", "checkout", "clean", "commit", "config",
                     "fetch", "init", "log", "merge", "pull", "push", "rebase",
                     "remote", "reset", "stash", "status", "submodule")
        if name in whitelist:
            return functools.partial(self.call, name)
        raise AttributeError("Git instance has no attribute '%s'" % name)

    def clone(self, *args, **kwargs):
        """ Wrapper for git clone """
        args = list(args)
        args.append(self.repo)
        kwargs["cwd"] = None
        return self.call("clone", *args, **kwargs)

    def update_submodules(self, raises=True):
        """ Update submodule, cloning them if necessary """
        # This will fail if some pushed a broken submodule
        # (ie git metadata does not match .gitmodules)
        res, out = self.submodule("status", raises=False)
        if res != 0:
            mess  = "Broken submodules configuration detected for %s\n" % self.repo
            mess += "git status returned %s\n" % out
            if raises:
                raise Exception(mess)
            else:
                return mess
        if not out:
            return
        res, out = self.submodule("update", "--init", "--recursive",
                            raises=False)
        if res == 0:
            return
        mess  = "Failed to update submodules\n"
        mess += out
        if raises:
            raise Exception(mess)
        return mess


    def get_local_branches(self):
        """ Get the list of the local branches in a dict
        master -> tracking branch

        """
        (status, out) = self.branch("--no-color", raises=False)
        if status != 0:
            mess  = "Could not get the list of local branches\n"
            mess += "Error was: %s" % out
            raise Exception(mess)
        lines = out.splitlines()
        # Remove the star and the indentation:
        return [x[2:] for x in lines]

    def is_valid(self):
        """Check if the worktree is a valid git tree."""
        if not os.path.isdir(self.repo):
            return False
        (status, out) = self.call("rev-parse", "--is-inside-work-tree", raises=False)
        return status == 0

    def get_status(self, untracked=True):
        """Return the output of status or None if it failed."""
        if untracked:
            (status, out) = self.status("--porcelain", raises=False)
        else:
            (status, out) = self.status("--porcelain", "--untracked-files=no", raises=False)

        return out if status == 0 else None

    def is_clean(self, untracked=True):
        """
        Returns true if working dir is clean.
        (ie no untracked files, no unstaged changes)

            :param untracked: will return True even if there are untracked files.
        """
        out = self.get_status(untracked)
        if out is None:
            return None

        lines = [l for l in out.splitlines() if len(l.strip()) != 0 ]
        if len(lines) > 0:
            return False
        return True

    def set_remote(self, name, url):
        """
        Set a new remote with the given name and url

        """
        # If it is already here, do nothing:
        in_conf = self.get_config("remote.%s.url" % name)
        if in_conf and in_conf == url:
            return
        self.remote("rm",  name, quiet=True, raises=False)
        self.remote("add", name, url, quiet=True)

    def set_tracking_branch(self, branch, remote_name, fetch_first=True, remote_branch=None):
        """ Update the configuration of a branch to track
        a given remote branch

        :param branch: the branch to set configuration for
        :param remote_name: the name of the remove ('origin' in most cases)
        :param remote_branch: the name of the remote to track. If not given
            will be the same of the branch name
        """
        if not branch in self.get_local_branches():
            self.branch(branch)
        if remote_branch is None:
            remote_branch = branch
        self.set_config("branch.%s.remote" % branch, remote_name)
        self.set_config("branch.%s.merge" % branch,
                        "refs/heads/%s" % remote_branch)

    def require_clean_worktree(self):
        """ Check that the git tree is clean
        :return: a string descrbing why we are not clean,
        or an empty sting if we are

        """
        # Taken from /usr/lib/git-core/git-sh-setup
        return ""

    def sync(self, git_project, branch_name=None,
             stash_first=False, rebase_devel=True):
        """ git pull --rebase on steroids:

         * abort if repo is not clean

         * update submodules and detect broken submodules configs

         * if no dev occured (master == origin/master),
           reset master to the remote

         * if on the correct branch, rebase it

         * if on a devel branch, and 'rebase_devel' is true,
           update the master branch and tries to rebase

        Return a tuple (status, message), where status can be:
            - None: sync was skipped, but there was no error
            - False: sync failed
            - True: sync suceeded
        """
        if branch_name is None:
            branch = git_project.default_branch
            if not branch:
                return None, "No branch given, and no branch configured by default"
        else:
            branch = git_project.get_branch(branch_name)

        current_branch = self.get_current_branch()
        if not current_branch:
            return None, "Not on any branch"

        if current_branch != branch.name and not rebase_devel:
            return None, "Not on the correct branch. " + \
                         "On %s but should be on %s" % (current_branch, branch.name)

        if not stash_first:
            error = self.require_clean_worktree()
            if error:
                return None, error

        with self.transaction() as transaction:
            if branch.tracks:
                self.fetch(branch.tracks)
                self.rebase(branch.name, branch.tracks)
            else:
                # No remote given, maybe this will work:
                self.fetch()
                self.rebase(branch_name)

        if transaction.ok:
            return True, ""
        else:
            return False,  transaction.output


    def __repr__(self):
        return "<Git repo in %s>" % self.repo



def get_repo_root(path):
    """Return the root dir of a git worktree given a path.

    :return None: if it's not a git work tree.
    """
    if os.path.isfile(path):
        path = os.path.dirname(path)
    if not os.path.isdir(path):
        return None

    git = Git(path)
    (ret, out) = git.call("rev-parse", "--show-toplevel", raises=False)

    return out.replace('/', os.sep) if ret == 0 else None

def is_submodule(path):
    """ Tell if the given path is a submodule

    """
    if not os.path.isdir(path):
        return False

    # Two cases:
    # * submodule not initialized -> path will be an empty dir
    # * submodule initialized  -> path/.git will be a file
    #   looking like:
    #       gitdir: ../../.git/modules/bar
    contents = os.listdir(path)
    if contents:
        dot_git = os.path.join(path, ".git")
        if os.path.isdir(dot_git):
            return False
        parent_repo_root = get_repo_root(os.path.dirname(path))
    else:
        parent_repo_root = get_repo_root(path)
    parent_git = Git(parent_repo_root)
    (retcode, out) = parent_git.submodule(raises=False)
    if retcode == 0:
        if not out:
            return False
        else:
            lines = out.splitlines()
            submodules = [x.split()[1] for x in lines]
            rel_path = os.path.relpath(path, parent_repo_root)
            return rel_path in submodules
    else:
        ui.warning("git submodules configuration is broken for",
                   parent_repo_root, "!",
                   "\nError was: ", ui.reset, "\n", "  " + out)
        return True

def is_git(path):
    """Return true if path is in a git work-tree."""
    return get_repo_root(path) == path

def get_git_projects(projects):
    """Return projects which are git projects."""
    git_projects = [p for p in projects if is_git(p.path)]
    return git_projects

class Transaction:
    """ Used to simplify chaining git commands """
    def __init__(self):
        self.ok = True
        self.output = ""
