class TemplateProject(object):
    def __init__(self, doc_worktree, worktree_project):
        self.doc_type = "template"
        self.name = "template"
        self.depends = list()
        self.src = worktree_project.src
        self.path = worktree_project.path
        self.doc_worktree = doc_worktree

    ##
    # Add self.doxfile_in, self.sphinx_conf_in, etc.

    def __repr__(self):
        return "<TemplateProject in %s>" % self.src
