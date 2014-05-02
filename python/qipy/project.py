import os

class PythonProject(object):
    def __init__(self, worktree, src, name):
        self.worktree = worktree
        self.src = src
        self.name  = name

    @property
    def path(self):
        return os.path.join(self.worktree.root, self.src)

    @property
    def setup_dot_py(self):
        return os.path.join(self.path, "setup.py")

    def __repr__(self):
        return "<%s in %s>" % (self.name, self.src)
