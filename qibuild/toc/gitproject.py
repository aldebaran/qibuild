import logging
from buildtool.git import Git

LOGGER = logging.getLogger("git")

class GitProject:
    """
    A git project is just a project versionned with git

    """

    def __init__(self, project):
        self.project = project
        self.git  = Git(self.project.get_src_dir())

    def fetch(self, *args):
        """
        fetch

        example:
        git.fetch(args=["origin"])

        """
        self.git.fetch(*args)

    def pull(self, *args):
        """ pull """
        self.git.pull(*args)

    def push(self, *args):
        """ push """
        self.git.push(*args)

    def status(self, *args):
        """ git status """
        if not self.git.is_clean():
            LOGGER.info("##################################")
            LOGGER.info("# %s" % (self.project.name))
            LOGGER.info("##################################")
            self.git.status(*args)
            return True
        return False

    def reset(self, *args):
        """
        reset working dir

        example:
        git.reset(args=["--hard", "origin/master"])
        """
        self.git.reset(*args)

    def checkout(self, branch, *args):
        """ checkout """
        self.git.checkout(branch, *args)

    def clean(self, *args):
        """
        clean working dir

        example:
        git.clean(args=["-fd"])
        """
        self.git.clean(*args)


    def clone(self, *args):
        """Clone the project, using URL from configuration """
        self.git.clone(*args)

    def is_clean(self):
        """
        Returns true if working dir is clean
        (nothing to commit, no untracked files)

        """
        return self.git.is_clean()


    def get_current_branch(self):
        """
        get current branch

        returns the current branch name

        """
        return self.git.get_current_branch()

    def get_current_remote_url(self):
        """
        returns the current remote url

        """
        return self.git.get_current_remote_url()

    def local_branches(self):
        """
        returns the list of the local branch names

        """
        return self.git.local_branches()

    def tag(self, *args):
        """ git tag """
        return self.git.tag(*args)
