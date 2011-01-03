##
## Copyright (C) 2009, 2010, 2011 Aldebaran Robotics
##

""" class that wrap git """

import os
import sys
import logging

from qitools           import command

GIT = "git"

if sys.platform.startswith("win32"):
    GIT = "C:\\Program Files\\Git\\bin\\git.exe"
    if not os.path.exists(GIT):
        GIT = "git"

class GitException(Exception):
    def __init__(self, *args):
        self.args = args

    def __str__(self):
        return repr(self.args)

class GitCommand:
    """ launch git command """
    logger = logging.getLogger("qibuild.git")

    def __init__(self, git_work_tree, git_dir=None):
        """
        warning: we use realpath for worktree and gitdir, because if we set GIT_WORK_TREE and GIT_DIR
        changing directory would make relative path invalid
        """
        self.worktree = os.path.realpath(git_work_tree)
        if git_dir:
            self.gitdir = git_dir
        else:
            self.gitdir = os.path.join(git_work_tree, ".git")
        self.gitdir = os.path.realpath(self.gitdir)

    def check_call(self, *args, **kargs):
        """ call a git command """
        git_env = None
        if not kargs.get("no_env", False):
            git_env                  = os.environ.copy()
            git_env['GIT_WORK_TREE'] = self.worktree
            git_env['GIT_DIR']       = self.gitdir
        margs = [ GIT ]
        margs.extend([ x for x in args])
        cwd = kargs.get("cwd", self.worktree)
        return command.check_call(margs, cwd = cwd, env = git_env)

    def call(self, *args, **kargs):
        """ call a git command """
        git_env = None
        if not kargs.get("no_env", False):
            git_env                  = os.environ.copy()
            git_env['GIT_WORK_TREE'] = self.worktree
            git_env['GIT_DIR']       = self.gitdir
        margs = [ GIT ]
        margs.extend([ x for x in args])
        cwd = kargs.get("cwd", self.worktree)
        return command.call(margs, cwd = cwd, env = git_env)

    def call_output(self, *args, **kargs):
        """ call a git command with output """
        git_env = None
        if not kargs.get("no_env", False):
            git_env                  = os.environ.copy()
            git_env['GIT_WORK_TREE'] = self.worktree
            git_env['GIT_DIR']       = self.gitdir
        margs = [ GIT ]
        margs.extend([ x for x in args])
        cwd = kargs.get("cwd", self.worktree)
        return command.call_output(margs, cwd = cwd, env = git_env)

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
    lines = command.call_output([GIT, "ls-remote", git_url])
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
        lines = self.cmd.call_output("symbolic-ref", ref)
        self.logger.debug("current.refs=" + str(lines[0]))
        return lines[0]

    def get_current_branch(self):
        """ return the current branch """
        branch = self.get_current_ref()[11:]
        self.logger.debug("current.branch=" + str(branch))
        return branch

    def get_current_remote_url(self):
        """
        use the origin of the current branch
        git config --get branch.master.remote
        """
        branch = self.get_current_branch()
        remote = self.cmd.call_output("config", "--get", "branch.%s.remote" % (branch))[0]
        if not remote:
            self.logger.warning("Current branch %s does not track any remote branch!" % \
                branch)
            return None
        try:
            url = self.cmd.call_output("config", "--get", "remote.%s.url" % (remote))[0]
        except command.CommandFailedException:
            try:
                url = self.cmd.call_output("config", "--get", "remote.origin.url")[0]
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

        remote = self.cmd.call_output("config", "--get", "branch.%s.remote" % (branch))[0].strip()
        merge = self.cmd.call_output("config", "--get", "branch.%s.merge" % (branch))[0].strip()
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


    def is_clean(self):
        """
        Returns true if working dir is clean.
        Nothing to commit, no untracked files
        /!\ : there could be a lot of false negatives ...
        """
        lines = self.cmd.call_output("status")
        # If work dir is clean, the output looks like:
        #    # on branch master
        #    # nothing to commit (working directory clean)
        # Strip commments:
        lines = [l for l in lines if not l.startswith("#")]
        if len(lines) > 2:
            return False
        if "working directory clean" in lines[0]:
            return True
        return False

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

def main():
    "Quick test"
    g = Git("/home/dmerejkowsky/src/appu_plugins/")
    g.set_tracking_branch("release", "release")
    g.set_tracking_branch("foo", "master", "foo", "git://foo.git")


if __name__ == "__main__":
    main()
