## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the WorkTree object.

"""

import os
import qisys.log
import operator

from qisys import ui
import qisys.sh
import qisys.qixml
from qisys.qixml import etree
import qisys.xml_parser

LOGGER = qisys.log.get_logger("WorkTree")


class NotInWorktree(Exception):
    """ Just a custom exception. """
    def __str__(self):
        return """ Could not guess worktree from current working directory
  Here is what you can do :
     - try from a valid work tree
     - specify an existing work tree with --work-tree PATH
     - create a new work tree with `qibuild init`
"""

class WorkTree:
    """ This class represent a :term:`worktree`. """
    def __init__(self, root):
        """
        Construct a new worktree

        :param root: The root directory of the worktree.
        """
        self.root = root
        self.projects = list()
        self.load()

    def load(self):
        """ Load the worktree.xml file. """
        self.projects = list()
        if not os.path.exists(self.worktree_xml):
            qisys.sh.mkdir(self.dot_qi)
            with open(self.worktree_xml, "w") as fp:
                fp.write("<worktree />\n")
        if os.path.exists(self.worktree_xml):
            self.xml_tree = qisys.qixml.read(self.worktree_xml)
            self.parse_projects()

        self.projects.sort(key=operator.attrgetter("src"))

    @property
    def dot_qi(self):
        """Get the dot_qi directory."""
        return os.path.join(self.root, ".qi")

    @property
    def worktree_xml(self):
        """Get the worktree_xml path."""
        return os.path.join(self.dot_qi, "worktree.xml")

    @property
    def qibuild_xml(self):
        """Get the path to qibuild.xml."""
        return os.path.join(self.dot_qi, "qibuild.xml")

    def get_manifest_projects(self):
        """ Get the projects mark as beeing 'manifest' projects. """
        manifest_projects = [p for p in self.projects if p.manifest]
        return manifest_projects

    def has_project(self, src):
        srcs = (p.src.lower() for p in self.projects)
        return src.lower() in srcs

    def update_project_config(self, src, key, value):
        """ Update the project configuration. """
        for elem in self.xml_tree.findall("project"):
            if elem.get("src") == src:
                elem.set(key, value)

    def set_manifest_project(self, src, profile="default"):
        """ Mark a project as being a manifest project. """
        project = self.get_project(src, raises=True)
        self.update_project_config(project.src, "manifest", "true")
        self.update_project_config(project.src, "profile", profile)
        self.dump()
        self.load()

    def set_git_project_config(self, src, remote, branch):
        """ Set the 'remote' and the 'branch' attributes of a
        project config so that `qisrc sync` can work afterwards

        """
        project = self.get_project(src, raises=True)
        self.update_project_config(project.src, "remote", remote)
        self.update_project_config(project.src, "branch", branch)
        self.dump()
        self.load()

    def set_project_review(self, src):
        """ Mark a project as being under code review. """
        project = self.get_project(src)
        self.update_project_config(project.src, "review", "true")
        self.dump()
        self.load()

    def dump(self):
        """ Dump self to the worktree.xml file. """
        qisys.sh.mkdir(self.dot_qi, recursive=True)
        qisys.qixml.write(self.xml_tree, self.worktree_xml)

    def parse_projects(self):
        """ Parse .qi/worktree.xml, resolve subprojects. """
        projects_elem = self.xml_tree.findall("project")
        for project_elem in projects_elem:
            project = Project(self, xml_elem=project_elem)
            project.parse()
            project.parse_qiproject_xml()
            self.projects.append(project)

        # Now parse the subprojects
        res = self.projects[:]
        for project in self.projects:
            self._rec_parse_sub_projects(project, res)
        self.projects = res[:]

    def _rec_parse_sub_projects(self, project, res):
        """ Recursively parse every project and subproject,
        filling up the res list.

        """
        if project.is_git():
            project.git_project = project
        for sub_project_src in project.subprojects:
            src = os.path.join(project.src, sub_project_src)
            src = qisys.sh.to_posix_path(src)
            sub_project = Project(self, src=src)
            sub_project.parse_qiproject_xml()
            if project.git_project:
                sub_project.git_project = project.git_project
            res.append(sub_project)
            self._rec_parse_sub_projects(sub_project, res)

    def get_project(self, src, raises=False):
        """ Get a project

        :param src: a absolute path, or a path relative to the worktree
        :param raises: Raises if project is not found
        :returns:  a :py:class:`Project` instance or None if raises is
            False and project is not found

        """
        src = to_relative_path(self.root, src)
        if not self.has_project(src):
            if not raises:
                return None
            mess  = "No project in '%s'\n" % src
            mess += "Known projects are in %s" % ", ".join([p.src for p in self.projects])
            raise Exception(mess)
        match = [p for p in self.projects if p.src == src]
        res = match[0]
        return res

    def add_project(self, src):
        """ Add a project to a worktree

        :param src: path to the project, can be absolute,
                    or relative to the worktree root

        """
        # Coming from user, can be an abspath:
        src = to_relative_path(self.root, src)
        if self.has_project(src):
            mess  = "Could not add project to worktree\n"
            mess += "Path %s is already registered\n" % src
            mess += "Current worktree: %s" % self.root
            raise Exception(mess)

        project = Project(self, src=src)
        root_elem = self.xml_tree.getroot()
        root_elem.append(project.xml_elem())
        self.dump()
        self.load()

    def remove_project(self, src, from_disk=False):
        """ Remove a project from a worktree

        :param src: path to the project, can be absolute,
                    or relative to the worktree root
        :param from_disk: also erase project files from disk


        """
        # Coming from user, can be an abspath:
        src = to_relative_path(self.root, src)
        if not self.has_project(src):
            raise Exception("No such project: %s" % src)
        root_elem = self.xml_tree.getroot()
        for project_elem in root_elem.findall("project"):
            if project_elem.get("src") == src:
                if from_disk:
                    to_remove = self.get_project(src).path
                    qisys.sh.rm(to_remove)
                root_elem.remove(project_elem)
        self.dump()
        self.load()

    def __repr__(self):
        res  = "<Worktree in %s\n" % self.root
        res += repr_list_projects(self.projects)
        res += ">\n"
        return res


def open_worktree(worktree=None):
    """
    Open a qi worktree.

    :return: a valid :py:class:`WorkTree` instance.
             If worktree is None, guess it from the current working dir.

    """
    if not worktree:
        worktree = guess_worktree()
    if worktree is None:
        raise NotInWorktree()
    if not os.path.exists(worktree):
        mess =  "Cannot open a worktree from %s\n" % worktree
        mess += "This path does not exist"
        raise Exception(mess)
    res = WorkTree(worktree)
    ui.debug("Opening worktree in", worktree)
    return res

def is_worktree(path):
    path = os.path.join(path, ".qi")
    return os.path.isdir(path)

def guess_worktree(cwd=None, raises=False):
    """Look for parent directories until a .qi dir is found somewhere."""
    if cwd is None:
        cwd = os.getcwd()
    head = cwd
    _tail = True
    while _tail:
        if is_worktree(head):
            return head
        (head, _tail) = os.path.split(head)
    if raises:
        raise NotInWorktree()
    else:
        return None

def create(directory, force=False):
    """Create a new Qi work tree in the given directory.

    If already in a worktre, will do nothing, unless
    force is True, and then will re-initialize the worktree.

    """
    if not force:
        parent_worktree = guess_worktree(directory)
        if parent_worktree and parent_worktree != directory:
            qisys.ui.warning("""{0} is already in a worktee
(in {1})
Use --force if you want to re-initialize the worktree""".format(directory, parent_worktree))
            return open_worktree(parent_worktree)

        git_project = git_project_path_from_cwd(directory)
        if git_project:
            mess  = "Trying to create a worktree inside a git project\n"
            mess += "(in %s)\n" % git_project
            raise Exception(mess)

    dot_qi = os.path.join(directory, ".qi")
    qisys.sh.mkdir(dot_qi, recursive=True)
    qi_xml = os.path.join(dot_qi, "qibuild.xml")
    if not os.path.exists(qi_xml) or force:
        with open(qi_xml, "w") as fp:
            fp.write("<qibuild />\n")
    return open_worktree(directory)

def git_project_path_from_cwd(cwd=None):
    """ Get the path to the git repo of the current project using cwd. """
    import qisrc.git
    if not cwd:
        cwd = os.getcwd()
    return qisrc.git.get_repo_root(cwd)

class Project(qisys.xml_parser.RootXMLParser):
    def __init__(self, worktree, src=None, xml_elem=None):
        qisys.xml_parser.RootXMLParser.__init__(self, xml_elem)
        self.worktree = worktree
        self.src = src
        self.git_project = None
        self.subprojects = list()
        self.manifest = False
        self.remote = "origin"
        self.branch = "master"
        self.profile = "default"
        self.review = False

    @property
    def path(self):
        """Give the path in native form."""
        path = os.path.join(self.worktree.root, self.src)
        return qisys.sh.to_native_path(path)

    @property
    def qiproject_xml(self):
        """Give the path to the qiproject.xml."""
        return os.path.join(self.path, "qiproject.xml")

    def _post_parse_attributes(self):
        self.check_needed("src")

    def parse_qiproject_xml(self):
        if not os.path.exists(self.qiproject_xml):
            return
        tree = qisys.qixml.read(self.qiproject_xml)
        project_elems = tree.findall("project")
        for project_elem in project_elems:
            src = qisys.qixml.parse_required_attr(project_elem, "src", xml_path=self.qiproject_xml)
            self.subprojects.append(src)

    def xml_elem(self):
        res = etree.Element("project")
        res.set("src", self.src)
        if self.git_project:
            res.set("git_project", self.git_project)
        if self.manifest:
            res.set("manifest", "true")
        if self.review:
            res.set("review", "true")
        if self.profile:
            res.set("profile", self.profile)
        if self.remote:
            res.set("remote", self.remote)
        if self.branch:
            res.set("branch", self.branch)
        return res

    def is_git(self):
        git_dir = os.path.join(self.path, ".git")
        return os.path.exists(git_dir)

    def __repr__(self):
        res  = "<Project in %s\n" % (self.src)
        res += "   path: %s\n" % (self.path)
        #res += "   git_project: %s\n" % (self.git_project)
        res += "   subprojects: %s\n" if len(self.subprojects) else ""
        res += "   is a manifest\n" if self.manifest else ""
        res += "   on %s/%s\n" % (self.remote, self.branch)
        res += "   profile: %s\n" % (self.profile)
        res += "   is reviewed\n" if self.review else ""
        res += ">\n"
        return res

def repr_list_projects(projects, name = "projects"):
    res = ""
    if len(projects):
        res += name
        for i, project in enumerate(projects):
            res += "(%s) %s, " % (i, project.src)
        res += "\n"
    return res

def to_relative_path(root, path):
    if os.path.isabs(path):
        path = os.path.relpath(path, start=root)
        path = qisys.sh.to_posix_path(path)
    return path
