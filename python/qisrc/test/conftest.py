# export all fixtures form qisys tests:
from qisys.test.conftest import *

import qisrc.git
import qisrc.worktree
import qisrc.manifest
import qisys.script

from qisrc.test.fake_git import FakeGit

class TestGitWorkTree(qisrc.worktree.GitWorkTree):
    """ A subclass of qisrc.worktree.WorkTree that
    can create git projects

    """
    def __init__(self, worktree=None):
        if not worktree:
            worktree = TestWorkTree()
        super(TestGitWorkTree, self).__init__(worktree)

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
        # where we will create worktrees and make our testing

    """

    def __init__(self, root):
        self.root = root
        self.srv = root.mkdir("srv")
        self.src = root.mkdir("src")
        self.work = root.mkdir("work")

        # Manifest itself can not be handled as a normal repo:
        self.create_repo("manifest.git", add_to_manifest=False)
        self.push_file("manifest.git", "manifest.xml", "<manifest />")
        manifest_xml = root.join("src", "manifest", "manifest.xml")
        self.manifest = qisrc.manifest.Manifest(manifest_xml.strpath)
        self.manifest.add_remote("origin", self.srv.strpath)
        self.manifest_url = self.srv.join("manifest.git").strpath

    def create_repo(self, project, src=None, add_to_manifest=True):
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

        if not add_to_manifest:
            return

        self.manifest.add_repo(project, src)
        repo = self.manifest.get_repo(project)

        manifest_repo = self.root.join("src", "manifest")
        git = qisrc.git.Git(manifest_repo.strpath)
        git.commit("--all", "--message", "add %s" % src)
        git.push("origin", "master:master")
        return repo

    def move_repo(self, project, new_src):
        """ Change a repo location """
        repo = self.manifest.get_repo(project)
        old_src = repo.src
        repo.src = new_src
        self.manifest.dump()
        self.push_manifest("%s: moved %s -> %s" % (project, old_src, new_src))
        self.manifest.load()

    def push_manifest(self, message):
        """ Push new manifest.xml version """
        manifest_repo = self.root.join("src", "manifest")
        git = qisrc.git.Git(manifest_repo.strpath)
        git.commit("--all", "--message", message)
        git.push("origin", "master:master")

    def remove_repo(self, project):
        """ Remove a repo from the manifest """
        self.manifest.remove_repo(project)
        self.push_manifest("removed %s" % project)

    def create_group(self, name, projects):
        """ Add a group to the manifest """
        for project in projects:
            self.create_repo(project)
        self.manifest.configure_group(name, projects)
        self.push_manifest("add group %s" % name)


    def push_file(self, project, filename, contents,
                  branch="master", force=False):
        """ Push a new file with the given contents to the given project
        It is assumed that the project has beed created

        """
        src = project.replace(".git", "")
        repo_src = self.src.join(src)
        to_write = repo_src.join(filename)
        if to_write.check(file=True):
            message = "Update %s" % filename
        else:
            message = "Add %s" % filename
        repo_src.join(filename).write(contents)
        git = qisrc.git.Git(repo_src.strpath)
        git.checkout("--force", "-B", branch)
        git.add(filename)
        if force:
            git.commit("--message", message, "--amend")
        else:
            git.commit("--message", message)
        if force:
            git.push("origin", "--force", "%s:%s" % (branch, branch))
        else:
            git.push("origin", "%s:%s" % (branch, branch))

class TestGit(qisrc.git.Git):
    """ the Git class with a few other helpfull methods """
    def __init__(self, repo=None):
        if repo is None:
            repo = os.getcwd()
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
        self.commit("--message", "initial commit")

    def read_file(self, path):
        """ Read the contents of a file """
        return self.root.join(path).read()

    def commit_file(self, path, contents, message=None):
        """ Commit a file. Path will be created if it does not exits """
        file_path = self.root.join(path)
        file_path.write(contents)
        if not message:
            message = "Create/update %s" % path
        self.add(path)
        self.commit("--message", message)


# pylint: disable-msg=E1101
@pytest.fixture
def git_worktree(cd_to_tmpdir):
    return TestGitWorkTree()

# pylint: disable-msg=E1101
@pytest.fixture
def test_git(request):
    return TestGit

# pylint: disable-msg=E1101
@pytest.fixture
def git_server(tmpdir):
    # pylint: disable-msg=E1101
    git_srv = TestGitServer(tmpdir.mkdir("git"))
    return git_srv

# pylint: disable-msg=E1101
@pytest.fixture
def mock_git(request):
    return FakeGit("repo")

# pylint: disable-msg=E1101
@pytest.fixture
def qisrc_action(cd_to_tmpdir):
    return QiSrcAction()

class QiSrcAction(TestAction):
    def __init__(self):
        super(QiSrcAction, self).__init__("qisrc.actions")
        self.root = self.worktree.root
        self.git_worktree = TestGitWorkTree(worktree=self.worktree)

    def create_git_project(self, src, branch="master"):
        return self.git_worktree.create_git_project(src, branch=branch)

    def reload_worktree(self):
        self.worktree = TestWorkTree(root=self.root)
        self.git_worktree = TestGitWorkTree(worktree=self.worktree)

    @property
    def tmpdir(self):
        return self.git_worktree.tmpdir

