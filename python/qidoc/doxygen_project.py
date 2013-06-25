import qidoc.project

class DoxygenProject(qidoc.project.DocProject):
    """  A doc projet using doxygen """
    def __init__(self, doc_worktree, project, name,
                 depends=None, dest=None):
        self.doc_type = "doxygen"
        super(DoxygenProject, self).__init__(doc_worktree, project, name,
                                             depends=depends, dest=dest)

    def configure(self):
        pass

    def build(self):
        pass

    def install(self, destdir):
        pass
