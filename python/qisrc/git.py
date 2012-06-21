## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" A Pythonic git API

"""
import os
import sys
import contextlib
import subprocess

import qibuild.config

class Git:
    """ The Git represent a git tree """
    def __init__(self, repo):
        """ :param repo: The path to the tree """
        self.repo = repo

    def call(self, *args, **kwargs):
        """
        Call a git command

        :param args: The arguments of the command.
                     For instance ["frobnicate", "--spam=eggs"]

        :param kwargs: Will be passed to subprocess.check_call()
                       command, with the following changes:

           * if cwd is not given it will be self.repo instead
           * if env is not given it will be read from the config file
           * if raises is False, no exception will be raise if command
             fails, and a (retcode, output) tuple will be returned.
        """
        build_env = qibuild.config.get_build_env()
        if not "cwd" in kwargs.keys():
            kwargs["cwd"] = self.repo
        if not "env" in kwargs.keys():
            kwargs["env"] = build_env
        if not "quiet" in kwargs.keys():
            kwargs["quiet"] = False
        cmd = ["git"]
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
            return (process.returncode, out)
        else:
            qibuild.command.call(cmd, **kwargs)

    def get_config(self, name):
        """ Get a git config value.
        Return None if not found

        """
        (status, out) = self.call("config", "--get", name,
            raises=False)
        if status != 0:
            return None
        return out.strip()

    def set_config(self, name, value):
        """ Set a new config value.
        Will be created if it does not exist
        """
        self.call("config", name, value)

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

    def add(self, *args, **kwargs):
        """ Wrapper for git add """
        return self.call("add", *args, **kwargs)

    def commit(self, *args, **kwargs):
        """ Wrapper for git commit """
        return self.call("commit", *args, **kwargs)

    def fetch(self, *args, **kwargs):
        """ Wrapper for git fetch """
        return self.call("fetch", *args, **kwargs)

    def init(self, *args, **kwargs):
        """ Wrapper for git init """
        return self.call("init", *args, **kwargs)

    def reset(self, *args, **kwargs):
        """ Wrapper for git reset """
        return self.call("reset", *args, **kwargs)

    def checkout(self, *args, **kwargs):
        """ Wrapper for git checkout """
        return self.call("checkout", *args, **kwargs)

    def pull(self, *args, **kwargs):
        """ Wrapper for git pull """
        return self.call("pull", *args, **kwargs)

    def clone(self, *args, **kwargs):
        """ Wrapper for git clone """
        args = list(args)
        args.append(self.repo)
        kwargs["cwd"] = None
        return self.call("clone", *args, **kwargs)

    def push(self, *args, **kwargs):
        """ Wrapper for git push """
        return self.call("push", *args, **kwargs)

    def remote(self, *args, **kwargs):
        """ Wrapper for git remote """
        return self.call("remote", *args, **kwargs)


    def get_local_branches(self):
        """ Get the list of the local branches in a dict
        master -> tracking branch

        """
        (status, out) = self.call("branch", "--no-color", raises=False)
        if status != 0:
            mess  = "Could not get the list of local branches\n"
            mess += "Error was: %s" % out
            raise Exception(mess)
        lines = out.splitlines()
        # Remove the star and the indentation:
        return [x[2:] for x in lines]

    def is_valid(self):
        """ Check if the worktree is a valid git tree
        """
        if not os.path.isdir(self.repo):
            return False
        (status, out) = self.call("show-ref", "--quiet", raises=False)
        return status == 0

    def is_clean(self, untracked=True):
        """
        Returns true if working dir is clean.
        (ie no untracked files, no unstaged changes)

            :param untracked: will return True even if there are untracked files.
        """
        if untracked:
            (status, out) = self.call("status", "-s", raises=False)
        else:
            (status, out) = self.call("status", "-suno", raises=False)
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
        self.call("remote", "rm",  name, quiet=True, raises=False)
        self.call("remote", "add", name, url, quiet=True)

    def set_tracking_branch(self, branch, remote_name, remote_branch=None):
        """
        Create a or update the configuration of a branch to track
        a given remote branch

        :param branch: the branch to be created, or to set configuration for
        :param remote_name: the name of the remove ('origin' in most cases)
        :param remote_branch: the name of the remote to track. If not given
            will be the same of the branch name

        """
        if remote_branch is None:
            remote_branch = branch
        # Fetch just in case the branch just has been created
        self.call("fetch", remote_name, quiet=True)

        # If the branch does not exist yet, create it at the right commit
        if not branch in self.get_local_branches():
            self.call("branch", branch, "%s/%s" % (remote_name, remote_branch),
                quiet=True)
        self.call("branch",
            "--set-upstream", branch, "%s/%s" % (remote_name, remote_branch),
             quiet=True)


    @contextlib.contextmanager
    def change_branch(self, branch):
        """ Change branch if not currently on the correct branch,
        then go back to where we were

        """
        current_branch = self.get_current_branch()
        if current_branch == branch:
            yield
            return
        with self.stash_changes():
            self.checkout(branch, quiet=True)
            yield
            self.checkout(current_branch, quiet=True)


    @contextlib.contextmanager
    def stash_changes(self):
        """ Stash changes, do something, then try to apply.

        If something went wrong, returns the error message
        """
        if self.is_clean(untracked=False):
            yield
            return
        self.call("stash", quiet=True)
        yield
        (retcode, out) = self.call("stash", "apply", quiet=True, raises=False)
        if retcode != 0:
            raise Exception(out)

    def update_branch(self, branch, remote_name, remote_branch=None):
        """ Update the given branch to match the given remote branch


        Return an string if something went wrong
        """
        if not remote_branch:
            remote_branch = branch
        remote_branch = "%s/%s" % (remote_name, remote_branch)
        if not self.get_current_branch():
            return "Not currently on any branch"
        if self.get_current_branch() != branch:
            return self.update_branch_if_ff(branch, remote_branch)
        try:
            with self.stash_changes():
                (retcode, out) = self.call("pull", "--rebase", raises=False)
                if retcode != 0:
                    self.call("rebase", "--abort", quiet=True, raises=False)
                    return out
                sys.stdout.write(out)
        except Exception, err:
            self.call("rebase", "--abort", quiet=True, raises=False)
            res = "Some unstaged changes were in conflict: "
            res +=  str(err)
            return res

    def update_branch_if_ff(self, local_branch, remote_branch):
        """ Update a local branch with a remote branch if the
        merge is fast-forward

        """
        self.fetch("--all", quiet=True)
        (retcode, out) = self.call("show-ref", "--verify",
            "refs/heads/%s" % local_branch,
            raises=False)
        if retcode != 0:
            return out
        local_sha1 = out.split()[0]
        (retcode, out) = self.call("show-ref", "--verify",
            "refs/remotes/%s" % remote_branch,
            raises=False)
        if retcode != 0:
            return out
        remote_sha1 = out.split()[0]
        (retcode, out) = self.call("merge-base", local_sha1, remote_sha1,
            raises=False)
        if retcode != 0:
            return out
        common_ancestor = out.strip()

        if common_ancestor != local_sha1:
            mess  = "Could not update %s with %s\n" % (local_branch, remote_branch)
            mess += "Merge is not fast-forward and you are not on %s" % local_branch
            return mess
        if local_sha1 == remote_sha1:
            # Nothing to do
            return
        # Safe to checkout the branch, run merge and then go back
        # to where we were:
        with self.change_branch(local_branch):
            print "Updating %s with %s ..." % (local_branch, remote_branch)
            self.call("merge", "-v", remote_sha1)


def open(repo):
    """ Open a new worktree
    """
    git = Git(repo)
    return git
