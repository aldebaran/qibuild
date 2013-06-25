import abc

class DocProject(object):

    __metaclass__ = abc.ABCMeta
    doc_type = None

    def __init__(self, doc_worktree, project, name, depends=None, dest=None):
        self.doc_worktree = doc_worktree
        self.name = name
        self.src = project.src
        self.path = project.path
        if not depends:
            depends = list()
        self.depends = list()
        self.dest = dest

    @abc.abstractmethod
    def configure(self):
        pass

    @abc.abstractmethod
    def build(self):
        pass

    @abc.abstractmethod
    def install(self, destdir):
        pass

    def __repr__(self):
        return "<%s %s in %s>" % (self.doc_type.capitalize() + "Project",
                                  self.name, self.src)

