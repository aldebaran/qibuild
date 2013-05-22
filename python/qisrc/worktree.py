import os

from qisys import ui
import qisys.worktree
import qisrc.git
import qisrc.sync
import qisrc.project

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
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = worktree.root
        self._root_xml = qisys.qixml.read(self.git_xml).getroot()
        worktree.register(self)
        self.git_projects = list()
        self.load_git_projects()
        self._syncer = qisrc.sync.WorkTreeSyncer(self)

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
        """ Delegates to WorkTreeSyncer """
        self._syncer.sync()

    def load_git_projects(self):
        """ Build a list of git projects using the
        xml configuration

        """
        self.git_projects = list()
        for worktree_project in self.worktree.projects:
            project_src = worktree_project.src
            if not qisrc.git.is_git(worktree_project.path):
                continue
            git_project = qisrc.project.GitProject(self, worktree_project)
            git_elem = self._get_elem(project_src)
            if git_elem is not None:
                git_project.load_xml(git_elem)
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

    def find_repo(self, repo):
        """ Look for a project configured with the given repo """
        for url in repo.urls:
            for git_project in self.git_projects:
                for remote in git_project.remotes:
                    if url == remote.url:
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
        git_project = qisrc.project.GitProject(self, worktree_project)
        git = qisrc.git.Git(git_project.path)
        git.clone(repo.default_remote.url, "--recursive",
                  "--branch", repo.default_branch,
                  "--origin", repo.default_remote.name)
        self.save_project_config(git_project)
        self.load_git_projects()

    def move_repo(self, repo, new_src):
        """ Move a project in the worktree (s-me remote url, different
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
        project_xml = project.dump_xml()
        self._set_elem(project.src, project_xml)
        qisys.qixml.write(self._root_xml, self.git_xml)

    def __repr__(self):
        return "<GitWorkTree in %s>" % self.root
