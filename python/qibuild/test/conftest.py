# Make all fixtures from qisys.test available to qibuild.test
from qisys.test.conftest import *

import qisys.worktree
import qibuild.worktree

class TestBuildWorkTree(qibuild.worktree.BuildWorktree):
    """ A subclass of qisrc.worktree.WorkTree that
    can create git projects

    """
    def __init__(self, root):
        worktree = qisys.worktree.create(root)
        super(TestBuildWorkTree, self).__init__(worktree)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
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
        self.worktree.add_project(src)

        xml = """ \
<project>
  <qibuild name="{name}" >
    <depends buildtime="true" runtime="false" names="{buildtime_names}" />
    <depends buildtime="false" runtime="true" names="{runtime_names}" />
  </qibuild>
</project>
"""
        xml = xml.format(name=name,
                        buildtime_names=" ".join(depends),
                        runtime_names=" ".join(rdepends),
                        )
        proj_path.join("qiproject.xml").write(xml)
        build_project = qibuild.worktree.BuildProject(proj_path.strpath)
        return build_project

@pytest.fixture
def build_worktree(request):
    tmp = tempfile.mkdtemp(prefix="tmp-test-worktree")
    def clean():
        qisys.sh.rm(tmp)
    request.addfinalizer(clean)
    wt = TestBuildWorkTree(tmp)
    return wt
