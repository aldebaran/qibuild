# export all fixtures form qisys tests:
from qisys.test.conftest import *

import qisrc.git
import qisrc.worktree
import qisrc.manifest

class TestGitWorkTree(qisrc.worktree.GitWorkTree):
    """ A subclass of qisrc.worktree.WorkTree that
    can create git projects

    """
    def __init__(self, root):
        worktree = qisys.worktree.create(root)
        super(TestGitWorkTree, self).__init__(worktree)
        self.root = root

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.root)

    def create_git_project(self, src, branch="master"):
        """ Create a new git project """
        to_make = os.path.join(self.root, src)
        qisys.sh.mkdir(to_make, recursive=True)
        test_git = TestGit(to_make)
        test_git.initialize(branch=branch)

        new_project = super(TestGitWorkTree, self).add_git_project(src)
        return new_project

class TestGitServer(object):
    """ Represent a set of git urls

    everything is done relative to the <root> parameter

<root>
  |__ srv
       # here be bare repos
       foo.git
       bar.git
  |__ src
        # temporary clones use to populate the
        # bare repos in srv/
        foo
        bar
 |__ work
        # where we will create worktrees anh make our testing

    """

    def __init__(self, root):
        self.root = root
        self.srv = root.mkdir("srv")
        self.src = root.mkdir("src")
        self.work = root.mkdir("work")
        manifest_xml = root.join("manifest.xml")
        manifest_xml.write("<manifest />")
        self.manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
        self.manifest.add_remote("origin", self.srv.strpath)

    def create_repo(self, project, src=None):
        """ Create a new repo and add it to the manifest """
        if not src:
            src = project.replace(".git", "")
        repo_srv = self.srv.mkdir(project)
        git = qisrc.git.Git(repo_srv.strpath)
        git.init("--bare")

        repo_src = self.src.mkdir(src)
        git = TestGit(repo_src.strpath)
        git.initialize()
        git.set_remote("origin", repo_srv.strpath)
        git.push("origin", "master:master")

        self.manifest.add_repo(project, src)
        repo = self.manifest.get_repo(project)
        return repo




class TestGit(qisrc.git.Git):
    """ the Git class with a few other helpfull methods """
    def __init__(self, repo):
        super(TestGit, self).__init__(repo)

    @property
    def root(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.repo)

    def initialize(self, branch="master"):
        """ Make sure there is at least one commit and one branch """
        self.init()
        self.checkout("-b", branch)
        self.root.join(".gitignore").write("")
        self.add(".gitignore")
        self.commit("-m", "initial commit")


# pylint: disable-msg=E1101
@pytest.fixture
def git_worktree(request):
    tmp = tempfile.mkdtemp(prefix="tmp-test-worktree")
    def clean():
        qisys.sh.rm(tmp)
    request.addfinalizer(clean)
    wt = TestGitWorkTree(tmp)
    return wt

# pylint: disable-msg=E1101
@pytest.fixture
def test_git(request):
    return TestGit

# pylint: disable-msg=E1101
@pytest.fixture
def git_server(request):
    tmp = tempfile.mkdtemp(prefix="tmp-test-git-srv")
    def clean():
        qisys.sh.rm(tmp)
    request.addfinalizer(clean)
    # pylint: disable-msg=E1101
    srv_root = py.path.local(tmp)
    git_srv = TestGitServer(srv_root)
    return git_srv
