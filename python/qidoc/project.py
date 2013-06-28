import abc
import os

import qisys.sh

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
        self.prebuild_script = None

    @abc.abstractmethod
    def configure(self, **kwargs):
        pass

    @abc.abstractmethod
    def build(self, **kwargs):
        pass

    @abc.abstractmethod
    def install(self, destdir):
        pass

    @property
    def build_dir(self):
        build_dir = os.path.join(self.path, "build-doc")
        qisys.sh.mkdir(build_dir)
        return build_dir

    @property
    def index_html(self):
        return os.path.join(self.build_dir, "html", "index.html")

    def __repr__(self):
        return "<%s %s in %s>" % (self.doc_type.capitalize() + "Project",
                                  self.name, self.src)

    def __eq__(self, other):
        return self.doc_type == other.doc_type and \
                self.src == other.src and \
                self.name == other.name

    def __ne__(self, other):
        return not self.__eq__(other)
