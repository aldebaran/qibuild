# export all fixtures form qisys tests:
from qisys.test.conftest import *

import qisrc.git

class TestGitWorkTree():
    """ A subclass of qisrc.worktree.WorkTree that
    can create git projects

    """
    def __init__(self, root):
        super(GitWorkTree, self).__init__(root)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.root)

    def create_project(self, src, branch="master", remote=None, review=False):
        """ Create a new git project """
        to_make = os.path.join(self.root, src)
        qisys.sh.mkdir(to_make, recursive=True)
        git = qisrc.git.Git(to_make)
        git.init()

        new_project = super(TestWorkTree, self).add_project(src,
                                                            branch=branch,
                                                            remote=remote,
                                                            review=review)

        return new_project

@pytest.fixture
def git_worktree(request):
    tmp = tempfile.mkdtemp(prefix="tmp-test-worktree")
    def clean():
        qisys.sh.rm(tmp)
    request.addfinalizer(clean)
    wt = TestGitWorkTree(tmp)
    return wt
