import os

import qisys.worktree

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

class GitWorkTree(qisys.worktree.WorkTree):
    """ Stores a list of git projects """
    def __init__(self, worktree):

        self.worktree = worktree
        self.root = worktree.root
        self._git_configs = self._load_git_configs()
        self.git_projects = self._load_git_projects()

    def _load_git_configs(self):
        """ Load the main xml config file """
        configs = dict()
        root = qisys.qixml.read(self.git_xml)
        for project_elem in root.findall("project"):
            src = project_elem.get("src")
            configs[src] = project_elem
        return configs

    def _load_git_projects(self):
        """ Build a list of git projects using the
        xml configuration

        """
        git_projects = list()
        for worktree_project in self.worktree.projects:
            project_src = worktree_project.src
            git_project = GitProject(self, project_src)
            git_elem = self._git_configs.get(project_src)
            if git_elem is not None:
                git_parser = GitProjectParser(git_project)
                git_parser.parse(git_elem)
            git_projects.append(git_project)
        return git_projects

    def get_git_project(self, path, raises=False, auto_add=False):
        """ Get a git project by its sources """
        src = self.worktree.normalize_path(path)
        for git_project in self.git_projects:
            if git_project.src == src:
                return git_project

    @property
    def git_xml(self):
        git_xml_path = os.path.join(self.dot_qi, "git.xml")
        if not os.path.exists(git_xml_path):
            with open(git_xml_path, "w") as fp:
                fp.write("""<git />""")
        return git_xml_path

    def __repr__(self):
        return "<GitWorkTree in %s>" % self.root


class GitProject(qisys.worktree.WorkTreeProject):
    def __init__(self, worktree, src):
        super(GitProject, self).__init__(worktree, src=src)
        self.branch = None
        self.remote = None
        self.review = False
        self.worktree = worktree

    def __repr__(self):
        return "<GitProject in {} ({})>".format(
            self.src, self.branch)

class Remote(object):
    def __init__(self):
        self.name = None
        self.url = None



##
# parsing

class RemoteParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(RemoteParser, self).__init__(target)

class GitProjectParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(GitProjectParser, self).__init__(target)

    def _parse_remote(self, elem):
        parser = RemoteParser(self.target.remote)
        parser.parse(elem)
