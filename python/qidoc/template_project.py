import os

class TemplateProject(object):
    def __init__(self, doc_worktree, worktree_project):
        self.doc_type = "template"
        self.name = "template"
        self.depends = list()
        self.src = worktree_project.src
        self.path = worktree_project.path
        self.doc_worktree = doc_worktree

    @property
    def sphinx_conf(self):
        in_path = os.path.join(self.path,
                               "sphinx", "conf.in.py")
        if not os.path.exists(in_path):
            return ""
        with open(in_path, "r") as fp:
            return fp.read()

    @property
    def themes_path(self):
        return  os.path.join(self.path, "sphinx", "_themes")

    def __repr__(self):
        return "<TemplateProject in %s>" % self.src
