class BuildWorktree(object):
    """

    """
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = self.worktree.root
        self.build_projects = list()

    def get_build_project(self, raises=True):
        pass

    def get_deps(self, project, runtime=False, build_beps_only=False):
        pass


class BuildProject:
    def __init__(self, path):
        self.path = path
        # read <qibuild> tag in qiproject.xml


