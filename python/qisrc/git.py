## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" class that wrap git """

import os
import sys
import logging
import subprocess

from qibuild           import command

class GitException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

GIT = None

def find_git():
    """ Find the Git executable """
    # FIXME: trusting path when on a cmd line makes sense,
    # but one day we may have a GUI calling qisrc...
    return command.find_program("git")

GIT = find_git()



class GitCommand:
    """ launch git command """
    logger = logging.getLogger("qibuild.git")

    def __init__(self, git_work_tree, git_dir=None):
        """
        """
        if not GIT:
            raise Exception("Could not find git executable !")

        # warning: we use realpath for worktree and gitdir,
        # because if we set GIT_WORK_TREE and GIT_DIR
        # changing directory would make relative path invalid
        self.worktree = os.path.realpath(git_work_tree)
        if git_dir:
            self.gitdir = git_dir
        else:
            self.gitdir = os.path.join(git_work_tree, ".git")
        self.gitdir = os.path.realpath(self.gitdir)

    def check_call(self, *args, **kargs):
        """ Call a git command """
        git_env = None
        if not kargs.get("no_env", False):
            git_env                  = os.environ.copy()
            git_env['GIT_WORK_TREE'] = self.worktree
            git_env['GIT_DIR']       = self.gitdir
        margs = [GIT]
        margs.extend([ x for x in args])
        cwd = kargs.get("cwd", self.worktree)
        return command.call(margs, cwd = cwd, env = git_env)

    def call(self, *args, **kargs):
        """ Call a git command, but do not throw if it fails

        """
        git_env = None
        if not kargs.get("no_env", False):
            git_env                  = os.environ.copy()
            git_env['GIT_WORK_TREE'] = self.worktree
            git_env['GIT_DIR']       = self.gitdir
        margs = [GIT]
        margs.extend([ x for x in args])
        cwd = kargs.get("cwd", self.worktree)
        return command.call(margs, cwd = cwd, env = git_env, ignore_ret_code=True)

    def call_output(self, *args, **kargs):
        """ call a git command with output
        kargs:
          - cwd
          - stderr (could be True or False, True by default)
          - rawout : return [ stdout, stderr ]
        """
        git_env = None
        if not kargs.get("no_env", False):
            git_env                  = os.environ.copy()
            git_env['GIT_WORK_TREE'] = self.worktree
            git_env['GIT_DIR']       = self.gitdir
        margs = [GIT]
        margs.extend([ x for x in args])
        cwd = kargs.get("cwd", self.worktree)
        wanterr = kargs.get("stderr", True)
        rawout  = kargs.get("rawout", False)
        stderrout = None if wanterr or not rawout else subprocess.PIPE
        stderrout = subprocess.PIPE
        process = subprocess.Popen(margs, cwd=cwd, env=git_env,
            stdout=subprocess.PIPE, stderr=stderrout)
        out = process.communicate()
        process.poll()
        if rawout:
            return (process.returncode,  out)
        return out[0].splitlines()

def git_open(git_work_tree, git_dir=None):
    """ open a git repository """
    return Git(git_work_tree, git_dir)

def _dict_from_refs(lines):
    """ return a dict from a git output (show-ref, ls-remote, ...)
    parses refs like:
    sha1   refs/bla/bla
    sha2   refs/bla/bla2

    return { 'refs/bla/bla'  : 'sha1',
             'refs/bla/bla2' : 'sha2' }
    """
    refs = dict()
    for line in lines:
        tmp = line.split()
        if (len(tmp) == 2):
            v = tmp[0].strip("\r\n\t ")
            k = tmp[1].strip("\r\n\t ")
            if v and k:
                refs[k] = v
    return refs

def get_remote_refs(git_url):
    """ return a dict with remote refs

    return { 'refs/bla/bla'  : 'sha1',
             'refs/bla/bla2' : 'sha2' }
    """
    git = command.find_program("git")
    if not git:
        raise Exception("git not found")
    process = subprocess.Popen([git, "ls-remote", git_url], stdout=subprocess.PIPE)
    out = process.communicate()[0]
    lines = out.splitlines()
    return _dict_from_refs(lines)

def get_remote_ref(git_url, ref='refs/heads/master'):
    """
    return the sha1 of a remote ref
    """
    refs = get_remote_refs(git_url)
    return refs.get(ref, None)

def extract_name_from_git_url(url):
    """ extract the git name from url

    >>> extract_name_from_git_url("git@yougit.com/paf/pifff.git")
    'pifff'

    >>> extract_name_from_git_url("git@yougit.com/paf/pifff")
    'pifff'

    >>> extract_name_from_git_url("git@yougit.com:pifff")
    'pifff'

    >>> extract_name_from_git_url("git@yougit.com:pifff.git")
    'pifff'

    >>> extract_name_from_git_url("git@yougit.com:paf/pifff.git")
    'pifff'

    """
    if url.endswith(".git"):
        url = url[:-4]
    #print "url:", url
    splitted = url.rsplit(":", 1)
    if len(splitted) == 2:
        url = splitted[1]
    splitted = url.rsplit("/", 1)
    if len(splitted) == 2:
        url = splitted[1]
    return url

class Git:
    """
    Store a list of ref
      for each ref:
        - tracking ref
        - actions
        - status
    """
    logger = logging.getLogger("qibuild.git")

    def __init__(self, git_work_tree, git_dir=None):
        self.cmd = GitCommand(git_work_tree, git_dir)
        self.project  = os.path.basename(git_work_tree)

    def is_valid(self):
        """
        Check if it's a valid git repo.
        return False if not valid
        """
        if not os.path.isdir(self.cmd.worktree) or not os.path.isdir(self.cmd.gitdir):
            return False
        try:
            self.cmd.check_call("show-ref", "--quiet")
        except command.CommandFailedException:
            return False
        return True

    def show_ref(self, *args):
        """
        parse each refs of a repository and return a dict
        """
        lines = self.cmd.call_output("show-ref", *args)
        return _dict_from_refs(lines)

    def list_branch_and_tracking(self):
        """ return a dict with (k, v) = (refs, remote_refs) """
        refs = dict()
        lines = self.cmd.call_output("for-each-ref",
                                     "--python",
                                     "--format=(%(refname), %(upstream))")
        for line in lines:
            if len(line) > 0:
                (k, v) = eval(line)
                if k.startswith("refs/heads"):
                    refs[k] = v
        return refs

    def local_branches(self):
        """ list all local branches """
        refs = self.list_branch_and_tracking()
        # Remove refs/heads/ from the list:
        return [x[11:] for x in refs.keys()]


    def get_current_ref(self, ref="HEAD"):
        """ return the current ref
        git symbolic-ref HEAD
        else: git name-rev --name-only --always HEAD
        """
        lines = self.cmd.call_output("symbolic-ref", ref, stderr=False)
        if len(lines) < 1:
            return None
        self.logger.debug("current.refs=" + str(lines[0]))
        return lines[0]

    def get_current_branch(self):
        """ return the current branch """
        branch = self.get_current_ref()
        if not branch:
            return branch
        self.logger.debug("current.branch=" + str(branch[11:]))
        return branch[11:]

    def get_current_remote_url(self):
        """
        use the origin of the current branch
        git config --get branch.master.remote
        """
        branch = self.get_current_branch()
        try:
            remote = self.cmd.call_output("config", "--get", "branch.%s.remote" % (branch), stderr=False)[0]
        except IndexError:
            return None
        if not remote:
            self.logger.debug("Current branch %s does not track any remote branch!" % \
                branch)
            return None
        try:
            url = self.cmd.call_output("config", "--get", "remote.%s.url" % (remote), stderr=False)[0]
        except command.CommandFailedException:
            try:
                url = self.cmd.call_output("config", "--get", "remote.origin.url", stderr=False)[0]
            except command.CommandFailedException:
                url = None
        self.logger.debug("remote=" + str(remote) + " ,url=" + str(url))
        return url

    def set_remote(self, url, name):
        """ set a git remote """
        # Remove section concerning the given remote, just in case:
        self.cmd.call("config", "--remove-section", "remote.%s" % name)

        self.cmd.check_call("config", "--add", "remote.%s.url" % name, url)

        self.cmd.check_call("config", "--add", "remote.%s.fetch" % name,
                            "+refs/heads/*:refs/remotes/%s/*" % name)

    def get_tracking_branch(self, branch=None):
        if not branch:
            branch = self.get_current_branch()

        try:
            remote = self.cmd.call_output("config", "--get", "branch.%s.remote" % (branch))[0].strip()
            merge = self.cmd.call_output("config", "--get", "branch.%s.merge" % (branch))[0].strip()
        except:
            return None
        if merge.startswith("refs/heads/"):
            return "%s/%s" % (remote, merge[11:])
        return None

    def set_tracking_branch(self, current_branch, remote_branch, remote=None, url=None):
        """Set the current tracking branch.
        If remote is not "origin", an new url must be given

        Useless with git>1.7 ?

        """
        if remote is not None and url is None:
            mess  = "git.set_tracking_branch "
            mess += "Remote is not None but no url was given"
            raise GitException(mess)

        if remote is not None:
            # Remove section concerning the given remote, just in case:
            self.cmd.call("config", "--remove-section", "remote.%s" % remote)

            self.cmd.check_call("config", "--add", "remote.%s.url" % remote,
                url)

            self.cmd.check_call("config", "--add", "remote.%s.fetch" % remote,
                "+refs/heads/*:refs/remote/%s/*" % remote)
        else:
            remote = "origin"

        # Remove section concerning the given branch, just in case:
        self.cmd.call("config", "--remove-section", "branch.%s" % current_branch)

        self.cmd.check_call("config", "--add",
            "branch.%s.remote" % current_branch,
            remote)

        self.cmd.check_call("config", "--add",
            "branch.%s.merge" % current_branch,
            "refs/heads/%s" % remote_branch)


    def is_clean(self, untracked=True):
        """
        Returns true if working dir is clean.
        Nothing to commit, no untracked files
        /!\ : there could be a lot of false negatives ...
        """
        if untracked:
            lines = self.cmd.call_output("status", "-s")
        else:
            lines = self.cmd.call_output("status", "-suno")
        lines = [l for l in lines if len(l.strip()) != 0 ]
        if len(lines) > 0:
            return False
        return True

    def update_only_ff(self, local_ref, remote_ref):
        """
        try to update a local_ref against a remote_ref,
        if that the merge wont apply => do nothing
        """
        refs = self.show_ref([local_ref, remote_ref])
        local_sha1  = refs[local_ref]
        remote_sha1 = refs[remote_ref]
        self.logger.debug("[" + self.project + "] try updating")
        self.logger.debug("[" + self.project + "] local :" + str(local_ref))
        self.logger.debug("[" + self.project + "] local :" + str(local_sha1))
        self.logger.debug("[" + self.project + "] remote:" + str(remote_ref))
        self.logger.debug("[" + self.project + "] remote:" + str(remote_sha1))

        if len(local_ref) == 0 or len(remote_ref) == 0:
            self.logger.debug("[" + self.project + "]"
                              + "local/remote refs missing : " "no update")
            return

        lines = self.cmd.call_output("merge-base", local_sha1, remote_sha1)
        self.logger.debug("merge-base: %s, local_sha1: %s, remote_sha1: %s",
                          lines, local_sha1, remote_sha1)
        if lines[0] != local_sha1:
            print "  /!\ Warning: could not update: ", self.project, " , not fast forward"
            return
        if self.get_current_ref() == local_ref:
            print "  /!\ Warning: this function wont change head"
        try:
            print "[" + self.project +  "] up:", local_ref[11:],
            print " <= ", remote_ref[13:]
            #fast-forward => simply write the new ref
            self.cmd.check_call("update-ref", local_ref, remote_ref)
        except command.CommandFailedException as e:
            print "  /!\ Warning: could not update: ", self.project, \
                  local_ref, ", return code is ", e.returncode


    def try_pull_rebase(self):
        """
        do the pull, but call rebase --abort when the pull fail
        """
        try:
            self.cmd.check_call("pull", "--rebase")
        except command.CommandFailedException as e:
            print "  /!\ Warning, could not update: ", self.project, \
                  ", return code:", e.returncode
        if os.path.isdir(os.path.join(self.cmd.worktree, ".git", "rebase-apply")):
            print "rebase fail => aborting the rebase"
            self.cmd.check_call("rebase", "--abort")

    def sync(self):
        """
        sync all branch of a repo
        """
        self.fetch()
        if os.path.isdir( os.path.join(self.cmd.worktree, ".git", "rebase-apply") ):
            print "[", self.project, "] rebase in progress.. abort"
            return
        refs = self.list_branch_and_tracking()
        for k, v in refs.iteritems():
            #self.logger.debug("ref[%s]: %s = %s", self.project, k, v)
            if self.get_current_ref() == k:
                self.logger.debug("try_pull_rebase : %s", k)
                self.try_pull_rebase()
            else:
                self.logger.debug("update_only_ff : %s", k)
                self.update_only_ff(k, v)


    def clone(self, *args):
        """ git clone """
        self.cmd.check_call("clone", *args, cwd = os.path.dirname(self.cmd.worktree), no_env=True)

    def fetch(self, *args):
        """ git fetch """
        self.cmd.check_call("fetch", *args)

    def push(self, *args):
        """ git push """
        self.cmd.check_call("push", *args)

    def pull(self, *args):
        """ git pull """
        self.cmd.check_call("pull", *args)

    def init(self, *args):
        """ git init """
        self.cmd.check_call("init", *args, no_env=True)

    def add(self, *args):
        """ git add """
        self.cmd.call("add", *args)

    def commit(self, *args):
        """ git commit """
        self.cmd.check_call("commit", *args)

    def status(self, *args):
        """ just call git status """
        return self.cmd.call("status", *args)

    def checkout(self, *args):
        """ git checkout """
        self.cmd.check_call("checkout", *args)

    def reset(self, ref, *args):
        """
        Reset to the given ref.

        Call fetch first just to be sure

        """
        # We always want ref, so it's not in *args.
        # But we want to run:
        # git reset [options] ref
        new_args = args + (ref,) # concatenation of tuples
        # pylint: disable-msg=W0142
        self.cmd.check_call("reset", *new_args)

    def clean(self, *args):
        """
        clean working dir

        examples:
        git.clean(args=["-fd"])
        git.clean(args=["-fdx"]) # also dele files in .gitignore
        """
        self.cmd.check_call("clean", *args)

    def tag(self, *args):
        """
        If tag is not signed, just tag it.
        Else, call tag -s.

        Note: if you want to sign your tag, be sure
        that ~/.gitconfig containg the same user.email and user.name
        as in your gpg key.

        Tag message will always be the name of the tag. (KISS)

        """
        self.cmd.check_call("tag", *args)


    def describe(self):
        """
        Call describe to get a nice version number

        """
        return self.cmd.call_output("describe", "--always", "--tags")[0]

# pylint: disable-msg=W0622,C0103
open = git_open
