from qisys.test.conftest import *
from qipy.test.conftest import *
from qibuild.test.conftest import QiBuildAction

class QiPkgAction(TestAction):
    def __init__(self):
        super(QiPkgAction, self).__init__("qipkg.actions")

    def add_test_project(self, src):
        this_dir = os.path.dirname(__file__)
        src_path = os.path.join(this_dir, "projects", src)
        dest_path = os.path.join(self.worktree.root, src)
        qisys.sh.copy_git_src(src_path, dest_path)

        worktree_project = self.worktree.add_project(src)
        return worktree_project

# pylint: disable-msg=E1101
@pytest.fixture
def qipkg_action(cd_to_tmpdir):
    res = QiPkgAction()
    return res
