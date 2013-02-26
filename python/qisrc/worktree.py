import os

import qisys.worktree

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

    def get_git_project(self, src, auto_add=False):
        """ Get a git project by its sources """
        worktree_project  = self.worktee.get_project(src, raises=False)
        # find the closest git project
        for git_project in self.git_projects:
            if src in

    @property
    def git_xml(self):
        git_xml_path = os.path.join(self.dot_qi, "git.xml")
        if not os.path.exists(git_xml_path):
            with open(git_xml_path, "w") as fp:
                fp.write("""<git />""")
        return git_xml_path


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
