import qisys.worktree

class BuildWorktree(qisys.worktree.WorkTreeObserver):
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

    def on_project_added(self, project):
        # create a new BuildProject if nessary, add it to the list
        # and re-compute the dependency tree
        pass

    def on_project_removed(self, project):
        # if the project that was removed was a qibuild project,
        # remove it and re-compute the dependency tree
        pass


class BuildProject(object)
    def __init__(self, path):
        self.path = path

    @property
    def qiproject_xml(self):
        return os.path.join(self.path, "qiproject.xml")
