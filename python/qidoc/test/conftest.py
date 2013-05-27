from qisys.test.conftest import *

import qidoc.worktree

class TestDocWorkTree(qidoc.worktree.DocWorkTree):
    """ A subclass of DocWorkTree that can create doc projects """

    def __init__(self, worktree=None):
        if not worktree:
            worktree = TestWorkTree()
        super(TestDocWorkTree, self).__init__(worktree)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1103
        return py.path.local(self.root)

    def create_doc_project(self, name, src=None, depends=None, doc_type="sphinx"):
        if not depends:
            depends = list()
        if not src:
            src = name
        proj_path = self.tmpdir.join(*src.split("/"))
        proj_path.ensure(dir=True)

        xml = """ \
<project version="3">
  <qidoc name="{0}" type="{1}">
    <depends names="{2}" />
  </qidoc>
</project>
"""
        xml = xml.format(name, doc_type, " ".join(depends))
        proj_path.join("qiproject.xml").write(xml)
        self.worktree.add_project(src)
        return self.get_doc_project(name)

    def create_sphinx_project(self, name, src=None, depends=None):
        return self.create_doc_project(name, src=src, depends=depends,
                                       doc_type="sphinx")
    def create_doxygen_project(self, name, src=None, depends=None):
        return self.create_doc_project(name, src=src, depends=depends,
                                       doc_type="doxygen")

    def add_test_project(self, src):
        """ Copy a project, reading sources from qidoc/test/projects

        Can return None when testing qidoc2 retro-compat

        """
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)

        worktree_project = self.worktree.add_project(src)
        doc_project = qidoc.worktree.new_doc_project(self, worktree_project)
        return doc_project

class QiDocAction(TestAction):
    def __init__(self):
        super(QiDocAction, self).__init__("qibuild.actions")
        self.doc_worktree = TestDocWorkTree()

    def add_test_project(self, *args, **kwargs):
        return self.doc_worktree.add_test_project(*args, **kwargs)

    def create_sphinx_project(self, *args, **kwargs):
        return self.doc_worktree.create_sphinx_project(*args, **kwargs)

    def create_doxygen_project(self, *args, **kwargs):
        return self.doc_worktree.create_doxygen_project(*args, **kwargs)

# pylint: disable-msg=E1103
@pytest.fixture
def doc_worktree(cd_to_tmpdir):
    return TestDocWorkTree()

# pylint: disable-msg=E1103
@pytest.fixture
def qidoc_action(cd_to_tmpdir):
    res = QiDocAction()
    return res

class QiBuildAction(TestAction):
    def __init__(self):
        super(QiBuildAction, self).__init__("qibuild.actions")
        self.build_worktree = TestBuildWorkTree()

