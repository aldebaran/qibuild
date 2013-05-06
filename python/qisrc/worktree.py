import os
import functools

from qisys import ui
import qisys.worktree
import qisrc.git
import qisrc.sync

class NotInAGitRepo(Exception):
    """ Custom exception when user did not
    specify any git repo ond the command line
    and we did not manage to guess one frome the
    working dir

    """
    def __str__(self):
        return """ Could not guess git repository from current working directory
  Here is what you can do :
     - try from a valid git repository
     - specify a repository path on the command line
"""


class GitWorkTree(qisys.worktree.WorkTreeObserver):
    """ Stores a list of git projects and a list of manifests """
    def __init__(self, worktree, sync_first=False):
        self.worktree = worktree
        self.root = worktree.root
        self._root_xml = qisys.qixml.read(self.git_xml).getroot()
        worktree.register(self)
        self.git_projects = list()
        self.load_git_projects()
        self._syncer = qisrc.sync.WorkTreeSyncer(self, sync_first=sync_first)

    def configure_manifest(self, name, manifest_url, groups=None, branch="master"):
        """ Add a new manifest to this worktree """
        self._syncer.configure_manifest(name, manifest_url, groups=groups, branch=branch)

    def remove_manifest(self, name):
        """ Remove the given manifest from this worktree """
        self._syncer.remove_manifest(name)

    def check_manifest(self, name, xml_path):
        """ Run a sync using just the xml file given as parameter """
        self._syncer.sync_from_manifest_file(name, xml_path)

    def sync(self):
        """ Load the manifests """
        self._syncer.sync_manifests()

    def load_git_projects(self):
        """ Build a list of git projects using the
        xml configuration

        """
        self.git_projects = list()
        for worktree_project in self.worktree.projects:
            project_src = worktree_project.src
            if not qisrc.git.is_git(worktree_project.path):
                continue
            git_project = GitProject(self, worktree_project)
            git_elem = self._get_elem(project_src)
            if git_elem is not None:
                git_parser = GitProjectParser(git_project)
                git_parser.parse(git_elem)
            self.git_projects.append(git_project)
            git_project.apply_config()

    def get_git_project(self, path, raises=False, auto_add=False):
        """ Get a git project by its sources """
        src = self.worktree.normalize_path(path)
        for git_project in self.git_projects:
            if git_project.src == src:
                return git_project
        if auto_add:
            self.worktree.add_project(path)
            return self.get_git_project(path)

    def find_url(self, remote_url):
        """ Look for a project configured with the given url """
        for git_project in self.git_projects:
            if git_project.clone_url == remote_url:
                return git_project


    @property
    def git_xml(self):
        git_xml_path = os.path.join(self.worktree.dot_qi, "git.xml")
        if not os.path.exists(git_xml_path):
            with open(git_xml_path, "w") as fp:
                fp.write("""<git />""")
        return git_xml_path

    @property
    def manifests(self):
        return self._syncer.manifests

    def add_git_project(self, src):
        """ Add a new git project """
        elem = qisys.qixml.etree.Element("project")
        elem.set("src", src)
        self._root_xml.append(elem)
        qisys.qixml.write(self._root_xml, self.git_xml)
        # This will trigger the call to self.load_git_projects()
        self.worktree.add_project(src)
        new_proj = self.get_git_project(src)
        return new_proj

    def on_project_removed(self, project):
        self.load_git_projects()

    def on_project_added(self, project):
        self.load_git_projects()

    def clone_missing(self, repo):
        """ Add a new project  """
        ui.info(ui.green, "Adding", repo.project, "->", repo.src)
        worktree_project = self.worktree.add_project(repo.src)
        # add_project caused self.load_git_projects() to be called,
        # but the path was not a valid git project yet
        # so the GitProject does not exist yet
        git_project = GitProject(self, worktree_project)
        git = qisrc.git.Git(git_project.path)
        git.clone(repo.remote_url, "--recursive",
                  "--branch", repo.default_branch,
                  "--origin", repo.remote)
        git_project.apply_remote_config(repo)
        self.save_project_config(git_project)
        self.load_git_projects()

    def move_repo(self, repo, new_src):
        """ Move a project in the worktree (same remote url, different
        src)

        """
        project = self.get_git_project(repo.src)
        ui.info(ui.warning, "Moving ", project.src, "to", new_src)
        new_path = os.path.join(self.root, new_src)
        if os.path.exists(new_path):
            ui.error(new_path, "already exists")
            ui.error("If you are sure there is nothing valuable here, "
                     "remove this directory and try again")
            return
        new_base_dir = os.path.dirname(new_path)
        try:
            qisys.sh.mkdir(new_base_dir, recursive=True)
            os.rename(project.path, new_path)
        except Exception as e:
            ui.error("Error when moving", project.src, "to", new_path,
                     "\n", e , "\n",
                     "Repository left in", project.src)
            return
        project.src = new_src
        self.save_project_config(project)

    def remove_repo(self, project):
        """ Remove a project from the worktree """
        ui.info(ui.green, "Removing", project.src)
        # not sure when to use from_disk here ...
        self.worktree.remove_project(project.src)


    def _get_elem(self, src):
        for xml_elem in self._root_xml.findall("project"):
            if xml_elem.get("src") == src:
                return xml_elem

    def _set_elem(self, src, new_elem):
        # remove it first if it exits
        for xml_elem in self._root_xml.findall("project"):
            if xml_elem.get("src") == src:
                self._root_xml.remove(xml_elem)
        self._root_xml.append(new_elem)

    def save_project_config(self, project):
        """ Save the project instance in .qi/git.xml """
        parser = GitProjectParser(project)
        project_xml = parser.xml_elem(node_name="project")
        self._set_elem(project.src, project_xml)
        qisys.qixml.write(self._root_xml, self.git_xml)

    def __repr__(self):
        return "<GitWorkTree in %s>" % self.root


class GitProject(object):
    def __init__(self, git_worktree, worktree_project):
        self.git_worktree = git_worktree
        self.src = worktree_project.src
        self.branches = list()
        self.remotes = list()

    @property
    def review(self):
        """ Wether the project is under code review """
        for remote in self.remotes:
            if remote.review:
                return True
        return False

    @property
    def default_branch(self):
        """ The default branch for this repository """
        for branch in self.branches:
            if branch.default:
                return branch

    @property
    def clone_url(self):
        """ The url to use when cloning this repository for
        the first time

        """
        default_branch = self.default_branch
        if not default_branch:
            return None
        tracked = default_branch.tracks
        if not tracked:
            return None
        for remote in self.remotes:
            if remote.name == tracked:
                return remote.url
        return None

    # pylint: disable-msg=E0213
    def change_config(func):
        """ Decorator for every function that changes the git configuration

        """
        @functools.wraps(func)
        def new_func(self, *args, **kwargs):
            # pylint: disable-msg=E1102
            res = func(self, *args, **kwargs)
            self.apply_config()
            self.git_worktree.save_project_config(self)
            return res
        return new_func

    @property
    def path(self):
        """ The full, native path to the underlying git repository """
        return os.path.join(self.git_worktree.root, self.src)


    @change_config
    def configure_remote(self, name, url=None):
        """ Configure a remote. If a remote with the same name
        exists, its url will be overwritten

        """
        remote_found = False
        for remote in self.remotes:
            if remote.name == name:
                remote_found = True
                if remote.url != url:
                    ui.warning("remote url changed", url, "->", remote.url)
                    remote.url = url
        if not remote_found:
            remote = Remote()
            remote.name = name
            remote.url = url
            self.remotes.append(remote)

    @change_config
    def configure_branch(self, name, tracks="origin",
                         remote_branch=None, default=True):
        """ Configure a branch. If a branch with the same name
        already exitsts, update its tracking remote.

        """
        if self.default_branch and self.default_branch.name != name:
            ui.warning("default branch changed",
                        self.default_branch.name, "->", name)
        branch_found = False
        for branch in self.branches:
            if branch.name == name:
                branch_found = True
                if branch.tracks != tracks:
                    ui.warning(branch.name, "now tracks", tracks,
                              "instead of", branch.tracks)
                    branch.tracks = tracks
                branch.default_branch = default
        if not branch_found:
            branch = Branch()
            branch.name = name
            branch.tracks = tracks
            branch.remote_branch = remote_branch
            branch.default = default
            self.branches.append(branch)
        return branch

    @change_config
    def apply_remote_config(self, repo):
        """ Apply the configuration read from the "repo" setting
        of a remote manifest.
        Called by WorkTreeSyncer

        """
        self.configure_branch(repo.default_branch, tracks=repo.remote,
                              remote_branch=repo.default_branch, default=True)
        self.configure_remote(repo.remote, repo.remote_url)

    def sync(self, branch_name=None, **kwargs):
        """ Synchronize remote changes with the underlying git repository
        Calls py:meth:`qisys.git.Git.sync`

        """
        git = qisrc.git.Git(self.path)
        if branch_name is None:
            branch = self.default_branch
            if not branch:
                return None, "No branch given, and no branch configured by default"
        else:
            branch = git.get_branch(branch_name)

        current_branch = git.get_current_branch()
        if not current_branch:
            return None, "Not on any branch"

        if current_branch != branch.name and not rebase_devel:
            return None, "Not on the correct branch. " + \
                         "On %s but should be on %s" % (current_branch, branch.name)

        return git.sync_branch(branch)


    def get_branch(self, branch_name):
        """ Get the branch matching the name
        :return: None if not found

        """
        for branch in self.branches:
            if branch.name == branch_name:
                return branch

    def apply_config(self):
        """ Apply configuration to the underlying git
        repository

        """
        git = qisrc.git.Git(self.path)
        for remote in self.remotes:
            git.set_remote(remote.name, remote.url)
        for branch in self.branches:
            git.set_tracking_branch(branch.name, branch.tracks,
                                    remote_branch=branch.remote_branch)


    def __repr__(self):
        return "<GitProject in %s>" % self.src

class Remote(object):
    def __init__(self):
        self.name = None
        self.url = None
        self.review = False

    def __repr__(self):
        res = "<Remote %s: %s" % (self.name, self.url)
        if self.review:
            res += " (review)"
        res += ">"
        return res

class Branch(object):
    def __init__(self):
        self.name = None
        self.tracks = None
        self.remote_branch = None
        self.default = False

    def __repr__(self):
        return "<Branch %s (tracks: %s)>" % (self.name, self.tracks)


##
# parsing

class RemoteParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(RemoteParser, self).__init__(target)
        self._required = ["name"]

class BranchParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(BranchParser, self).__init__(target)
        self._required = ["name"]

class GitProjectParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GitProjectParser, self).__init__(target)
        self._ignore = ["worktree", "path", "review", "clone_url"]
        self._required = ["src"]

    def _parse_remote(self, elem):
        remote = Remote()
        parser = RemoteParser(remote)
        parser.parse(elem)
        self.target.remotes.append(remote)

    def _parse_branch(self, elem):
        branch = Branch()
        parser = BranchParser(branch)
        parser.parse(elem)
        self.target.branches.append(branch)

    def _write_branches(self, elem):
        for branch in self.target.branches:
            parser = BranchParser(branch)
            branch_xml = parser.xml_elem()
            elem.append(branch_xml)

    def _write_remotes(self, elem):
        for remote in self.target.remotes:
            parser = RemoteParser(remote)
            remote_xml = parser.xml_elem()
            elem.append(remote_xml)
