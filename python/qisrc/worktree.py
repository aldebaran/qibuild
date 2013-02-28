import os

import qisys.worktree
import qisrc.git

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

def open_git_worktree(root):
    """ Open an existing GitWorkTree """
    worktree = qisys.worktree.open_worktree(root)
    git_worktree = GitWorkTree(worktree)
    return git_worktree

class GitWorkTree(qisys.worktree.WorkTreeObserver):
    """ Stores a list of git projects """
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = worktree.root
        self._root_xml = qisys.qixml.read(self.git_xml).getroot()
        self._load()
        worktree.register(self)

    def _load(self):
        self.git_projects = self._load_git_projects()

    def _load_git_projects(self):
        """ Build a list of git projects using the
        xml configuration

        """
        git_projects = list()
        for worktree_project in self.worktree.projects:
            project_src = worktree_project.src
            if not qisrc.git.is_git(worktree_project.path):
                continue
            git_project = GitProject(self, worktree_project)
            git_elem = self._get_elem(project_src)
            if git_elem is not None:
                git_parser = GitProjectParser(git_project)
                git_parser.parse(git_elem)
            git_projects.append(git_project)
            git_project.apply_config()
        return git_projects

    def get_git_project(self, path, raises=False, auto_add=False):
        """ Get a git project by its sources """
        src = self.worktree.normalize_path(path)
        for git_project in self.git_projects:
            if git_project.src == src:
                return git_project

    @property
    def git_xml(self):
        git_xml_path = os.path.join(self.worktree.dot_qi, "git.xml")
        if not os.path.exists(git_xml_path):
            with open(git_xml_path, "w") as fp:
                fp.write("""<git />""")
        return git_xml_path

    def add_git_project(self, src):
        """ Add a new git project """
        elem = qisys.qixml.etree.Element("project")
        elem.set("src", src)
        self._root_xml.append(elem)
        qisys.qixml.write(self._root_xml, self.git_xml)
        # This will trigger the call to self._load()
        self.worktree.add_project(src)
        new_proj = self.get_git_project(src)
        return new_proj

    def on_project_removed(self, project):
        self._load()

    def on_project_added(self, project):
        self._load()

    def _get_elem(self, src):
        for xml_elem in self._root_xml.findall("project"):
            if xml_elem.get("src") == src:
                return xml_elem

    def _set_elem(self, src, new_elem):
        for xml_elem in self._root_xml.findall("project"):
            if xml_elem.get("src") == src:
                self._root_xml.remove(xml_elem)
                self._root_xml.append(new_elem)

    def on_git_config_changed(self, project):
        parser = GitProjectParser(project)
        project_xml = parser.xml_elem(node_name="project")
        self._set_elem(project.src, project_xml)
        qisys.qixml.write(self._root_xml, self.git_xml)

    def __repr__(self):
        return "<GitWorkTree in %s>" % self.root


class GitProject(object):
    def __init__(self, git_worktree, worktree_project):
        self.git_worktree = git_worktree
        self.path = worktree_project.path
        self.src = worktree_project.src
        self.branches = list()
        self.remotes = list()

    def change_config(func):
        """ Decorator for every function that changes the git configuration

        """
        def new_func(self, *args, **kwargs):
            res = func(self, *args, **kwargs)
            self.apply_config()
            self.git_worktree.on_git_config_changed(self)
            return res
        return new_func

    @change_config
    def add_remote(self, name, url=None):
        remote = Remote()
        remote.name = name
        remote.url = url
        self.remotes.append(remote)

    @change_config
    def add_branch(self, name, tracks=None, remote_branch=None):
        branch = Branch()
        branch.name = name
        branch.tracks = tracks
        branch.remote_branch = remote_branch
        self.branches.append(branch)
        self.apply_config()
        self.git_worktree.on_git_config_changed(self)

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



    @property
    def review(self):
        for remote in self.remotes:
            if remote.review:
                return True
        return False

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
        self._ignore = ["worktree", "path", "review"]
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
