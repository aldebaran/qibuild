## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import copy
import operator

from qisys import ui
import qisys.worktree
import qisrc.git
import qisrc.snapshot
import qisrc.sync
import qisrc.project

class NotInAGitRepo(Exception):
    """ Custom exception when user did not
    specify any git repo ond the command line
    and we did not manage to guess one from the
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

    def configure_manifest(self, manifest_url, groups=None, all_repos=False,
                           branch="master", ref=None, review=None, force=False):
        """ Add a new manifest to this worktree """
        return self._syncer.configure_manifest(manifest_url, groups=groups,
                                               branch=branch, ref=ref, review=review,
                                               force=force, all_repos=all_repos)

    def configure_projects(self, projects):
        self._syncer.configure_projects(projects)

    def check_manifest(self, xml_path):
        """ Run a sync using just the xml file given as parameter """
        return self._syncer.sync_from_manifest_file(xml_path)

    def sync(self):
        """ Delegates to WorkTreeSyncer """
        return self._syncer.sync()

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

    def get_git_project(self, path, raises=False, auto_add=False):
        """ Get a git project by its sources """
        src = self.worktree.normalize_path(path)
        for git_project in self.git_projects:
            if git_project.src == src:
                return git_project
        if auto_add:
            self.worktree.add_project(path)
            return self.get_git_project(path)
        if raises:
            raise NoSuchGitProject(src)

    def get_git_projects(self, groups=None):
        """ Get the git projects matching a given group """
        if not groups:
            return self.git_projects
        res = set()
        git_project_names = dict()
        group_names = groups
        for git_project in self.git_projects:
            git_project_names[git_project.name] = git_project
        projects = list()
        groups = qisrc.groups.get_groups(self.worktree)
        for group_name in group_names:
            warn_for_group = True
            project_names = groups.projects(group_name)
            for project_name in project_names:
                git_project = git_project_names.get(project_name)
                if git_project:
                    res.add(git_project)
                else:
                    if warn_for_group:
                        ui.warning("Group", group_name, "is not currently in use\n",
                                   "Please use `qisrc add-group %s`" % group_name)
                        warn_for_group = False

        res = list(res)
        res.sort(key=operator.attrgetter("src"))
        return res

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
    def manifest(self):
        return self._syncer.manifest

    def snapshot(self):
        """ Return a :py:class`.Snapshot` of the current worktree state

        """
        snapshot = qisrc.snapshot.Snapshot()
        snapshot.manifest = self.manifest
        git = qisrc.git.Git(self._syncer.manifest_repo)
        rc, out = git.call("rev-parse", "HEAD", raises=False)
        snapshot.manifest.ref = out
        for git_project in self.git_projects:
            src = git_project.src
            git = qisrc.git.Git(git_project.path)
            rc, out = git.call("rev-parse", "HEAD", raises=False)
            if rc != 0:
                ui.error("git rev-parse HEAD failed for", src)
                continue
            snapshot.refs[src] = out.strip()
        return snapshot

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

    def reload(self):
        self.load_git_projects()

    def clone_missing(self, repo):
        """ Add a new project.
        :returns: a boolean telling if the clone succeeded

        """
        worktree_project = self.worktree.add_project(repo.src)
        git_project = qisrc.project.GitProject(self, worktree_project)
        if os.path.exists(git_project.path):
            git = qisrc.git.Git(git_project.path)
            git_root = qisrc.git.get_repo_root(git_project.path)
            if not git_root == git_project.path:
                # Nested git projects:
                return self._clone_missing(git_project, repo)
            if git.is_valid() and git.is_empty():
                ui.warning("Removing empty git project in", git_project.src)
                qisys.sh.rm(git_project.path)
            else:
                # Do nothing, the remote will be re-configured later
                # anyway
                return True
        return self._clone_missing(git_project, repo)

    def _clone_missing(self, git_project, repo):
        branch = repo.default_branch
        clone_url = repo.clone_url
        qisys.sh.mkdir(git_project.path, recursive=True)
        git = qisrc.git.Git(git_project.path)
        remote_name = repo.default_remote.name
        try:
            git.init()
            git.remote("add", remote_name, clone_url)
            git.fetch(remote_name, "--quiet")
            git.checkout("-b", branch, "%s/%s" % (remote_name, branch))
        except:
            ui.error("Cloning repo failed")
            if git.is_empty():
                qisys.sh.rm(git_project.path)
            self.worktree.remove_project(repo.src)
            return False
        self.save_project_config(git_project)
        self.load_git_projects()
        return True

    def move_repo(self, repo, new_src, force=False):
        """ Move a project in the worktree (same remote url, different
        src)

        """
        project = self.get_git_project(repo.src)
        if not project:
            return
        ui.info("* moving", ui.blue, project.src,
                ui.reset, "to", ui.blue, new_src)
        new_path = os.path.join(self.worktree.root, new_src)
        new_path = qisys.sh.to_native_path(new_path)
        if os.path.exists(new_path):
            if force:
                qisys.sh.rm(new_path)
            else:
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
        self.worktree.move_project(project.src, new_src)
        project.src = new_src
        self.save_project_config(project)
        return True

    def checkout(self, branch, force=False):
        """ Called by ``qisrc checkout``

        For each project, checkout the branch if it is different than
        the default branch of the manifest.

        """
        ui.info(ui.green, ":: Checkout projects ...")
        errors = list()
        manifest_xml = os.path.join(self._syncer.manifest_repo, "manifest.xml")
        manifest = qisrc.manifest.Manifest(manifest_xml)
        to_checkout = list()
        for project in self.git_projects:
            if project.default_branch is None:
                continue
            branch_name = project.default_branch.name
            git = qisrc.git.Git(project.path)
            if git.get_current_branch() != branch_name:
                to_checkout.append(project)

        n = len(to_checkout)
        if n == 0:
            ui.info(ui.green, "Nothing to checkout")
            return True

        max_src = max([len(x.src) for x in to_checkout])
        for i, project in enumerate(to_checkout):
            ui.info_count(i, n, ui.bold, "Checkout",
                         ui.reset, ui.blue, project.src.ljust(max_src), end="\r")
            if project.default_branch is None:
                continue
            branch_name = project.default_branch.name
            remote_name = project.default_remote.name
            git = qisrc.git.Git(project.path)
            ok, err = git.safe_checkout(branch_name, remote_name, force=force)
            if not ok:
                errors.append((project.src, err))
        if not errors:
            return True
        ui.error("Failed to checkout some projects")
        for (project, error) in errors:
            ui.info(project, ":", error)
        return False

    def get_projects_on_branch(self, branch):
        """ Return a dict (src, project) for every project as configured
        on the given branch of the manifest.

        """
        res = dict()
        ref = "origin/" + branch
        manifest = qisrc.manifest.from_git_repo(self._syncer.manifest_repo, ref)
        if not manifest:
            raise Exception("Could not read manifest on %s"% ref)
        groups = self._syncer.manifest.groups
        repos = manifest.get_repos(groups=groups)
        for repo in repos:
            project = self.find_repo(repo)
            if project:
                # Make a copy so that we do not modify the projects in place
                project_copy = copy.deepcopy(project)
                project_copy.read_remote_config(repo, quiet=True)
                res[project_copy.src] = project_copy
        return res

    def remove_repo(self, project):
        """ Remove a project from the worktree """
        ui.info(ui.green, "Removing", project.src)
        # not sure when to use from_disk here ...
        if project in self.worktree.projects:
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

    def save_git_config(self):
        """ Save the worktree config in .qi/git.xml """
        for project in self.git_projects:
            project_xml = project.dump_xml()
            self._set_elem(project.src, project_xml)
        qisys.qixml.write(self._root_xml, self.git_xml)

    def __repr__(self):
        return "<GitWorkTree in %s>" % self.root

def on_no_matching_projects(worktree, groups=None):
    """ What to do when we find an empty worktree """
    if groups and len(groups) > 1:
        mess = """The groups {groups} do not contain any project in the worktree {worktree.root}."""
    elif groups and len(groups) == 1:
        groups = groups[0]
        mess = """The group {groups} does not contain any project in the worktree {worktree.root}."""
    else:
        mess = """The worktree in {worktree.root}
does not contain any project."""
    tips = """
Tips:
    * Use `qisrc init` to fetch some sources from a remote manifest
    * Use `qisrc add` to register a new project path to this worktree
"""
    ui.warning(mess.format(worktree=worktree, groups=groups) + tips)

class NoSuchGitProject(Exception):
    pass
