# Make all fixtures from qisys.test available to qibuild.test
from qisys.test.conftest import *
from qitoolchain.test.conftest import *

import qisys.worktree
import qibuild.worktree

class TestBuildWorkTree(qibuild.worktree.BuildWorkTree):
    """ A subclass of qisrc.worktree.WorkTree that
    can create git projects

    """
    def __init__(self, worktree=None):
        if not worktree:
            worktree = TestWorkTree()
        super(TestBuildWorkTree, self).__init__(worktree)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1103
        return py.path.local(self.root)

    def create_project(self, name, src=None, depends=None, rdepends=None):
        """ Create a new build project """
        if not depends:
            depends = list()
        if not rdepends:
            rdepends = list()
        if not src:
            src = name
        proj_path = self.tmpdir.mkdir(src)

        # FIXME: use new syntax
        xml = """ \
<project name="{name}" >
  <depends buildtime="true" runtime="false" names="{buildtime_names}" />
  <depends buildtime="false" runtime="true" names="{runtime_names}" />
</project>
"""
        xml = xml.format(name=name,
                        buildtime_names=" ".join(depends),
                        runtime_names=" ".join(rdepends),
                        )
        proj_path.join("qiproject.xml").write(xml)
        cmake = """ \
cmake_minimum_required(VERSION 2.8)
project({name} C)
find_package(qibuild)
qi_create_bin({name} main.c)

"""
        cmake = cmake.format(name=name)
        main_c = """ \
int main()
{
  return 0;
}
"""
        proj_path.join("CMakeLists.txt").write(cmake)
        proj_path.join("main.c").write(main_c)
        self.worktree.add_project(src)
        return self.get_build_project(src)

    def add_test_project(self, src, name=None):
        """ Copy a project, reading the sources
        from qibuild/test/projects

        """
        if not name:
            name = os.path.basename(src)
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.root, src)
        qisys.sh.install(src_path, dest_path)
        self.worktree.add_project(src)
        # using raises=False for convert tests
        return self.get_build_project(name, raises=False)



# pylint: disable-msg=E1103
@pytest.fixture
def build_worktree(cd_to_tmpdir):
    return TestBuildWorkTree()

# pylint: disable-msg=E1103
@pytest.fixture
def qibuild_action(cd_to_tmpdir):
    res = QiBuildAction()
    return res

class QiBuildAction(TestAction):
    def __init__(self):
        super(QiBuildAction, self).__init__("qibuild.actions")
        self.build_worktree = TestBuildWorkTree()

    def add_test_project(self, name):
        """ Add a test project using a project path in
        <this_dir>/projects/

        """
        return self.build_worktree.add_test_project(name)

    def create_project(self, name, **kwargs):
        """ Delegates to TestBuildWorkTree.create_project """
        return self.build_worktree.create_project(name, **kwargs)

    def reload_worktree(self):
        """ Reload the worktree. Useful when an *other* BuildWorkTree
        has changed the cache

        """
        self.build_worktree = TestBuildWorkTree()

    @property
    def tmpdir(self):
        return self.build_worktree.tmpdir
