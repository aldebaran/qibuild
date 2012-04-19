## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the WorkTree object.

"""

import os
import logging
import operator

import qibuild.sh
import qixml
from qixml import etree

LOGGER = logging.getLogger("WorkTree")

class WorkTree:
    """ This class represent a :term:`worktree`

    """
    def __init__(self, root):
        """
        Construct a new worktree

        :param root: The root directory of the worktree.
        """
        self.root = root
        self.projects = list()
        self.git_projects = list()
        self.buildable_projects = list()
        self.load()

    def load(self):
        """
        Load the worktree.xml file

        """
        self.projects = list()
        self.git_projects = list()
        self.buildable_projects = list()
        dot_qi = os.path.join(self.root, ".qi")
        worktree_xml = os.path.join(dot_qi, "worktree.xml")
        if not os.path.exists(worktree_xml):
            qibuild.sh.mkdir(dot_qi)
            with open(worktree_xml, "w") as fp:
                fp.write("<worktree />\n")
        if os.path.exists(worktree_xml):
            self.xml_tree = qixml.read(worktree_xml)
            self.parse_projects()
            self.parse_git_projects()
            self.parse_buildable_projects()

    def get_manifest_projects(self):
        """ Get the projects mark as beeing 'manifest' projects

        """
        return [p for p in self.projects if p.manifest]

    def set_manifest_project(self, src):
        """ Mark a project as being a manifest project

        """
        project = self.get_project(src)
        project.manifest = True
        project_elems = self.xml_tree.findall("project")
        for project_elem in project_elems:
            if project_elem.get("src") == src:
                project_elem.set("manifest", "true")
                break
        self.dump()
        self.load()

    def dump(self):
        """
        Dump self to the worktree.xml file

        """
        dot_qi = os.path.join(self.root, ".qi")
        qibuild.sh.mkdir(dot_qi, recursive=True)
        worktree_xml = os.path.join(self.root, ".qi", "worktree.xml")
        qixml.write(self.xml_tree, worktree_xml)

    def parse_projects(self):
        """ Parse .qi/worktree.xml
        and returns a lits of Projects instances
        """
        projects_elem = self.xml_tree.findall("project")
        for project_elem in projects_elem:
            project = Project()
            project.parse(project_elem)
            p_path = os.path.join(self.root, project.src)
            project.path = qibuild.sh.to_native_path(p_path)
            if os.path.exists(os.path.join(project.path, ".git")):
                project.git_project = project
                self.git_projects.append(project)
            self.projects.append(project)
        self.git_projects.sort(key=operator.attrgetter("src"))
        self.projects.sort(key=operator.attrgetter("src"))


    def parse_git_projects(self):
        """ Iterate through every project.

        If project is a git directory, add it to the list.
        If not, look at the config and search of a matching project

        """
        projects_elem = self.xml_tree.findall("project")
        for project_elem in projects_elem:
            p_src = project_elem.get("src")
            git_project_src = project_elem.get("git_project")
            if git_project_src:
                project = self.get_project(p_src)
                git_project = self.get_project(git_project_src)
                project.git_project = git_project

    def parse_buildable_projects(self):
        """ Iterate through every project.

        If project contains a qirpoject.xml and a CMakeLists.txt
        file, add it to the list

        """
        for project in self.projects:
            p_path = project.path
            qiproj_xml = os.path.join(p_path, "qiproject.xml")
            cmake_lists = os.path.join(p_path, "CMakeLists.txt")
            if os.path.exists(qiproj_xml) and \
                os.path.exists(cmake_lists):
                self.buildable_projects.append(project)

    def get_project(self, src, raises=False):
        """
        Get a project.
        :param src: a absolute path, or a path relative to the worktree
        :param raises: Raises if project is not found
        :returns:  a :py:class:`Project` instance or None if raises is
            False and project is not found

        """
        if os.path.isabs(src):
            src = os.path.relpath(src, self.root)
            src = qibuild.sh.to_posix_path(src)
        p_srcs = [p.src for p in self.projects]
        if not src in p_srcs:
            if not raises:
                return None
            mess  = "No project in '%s'\n" % src
            mess += "Know projects are in %s" % ", ".join(p_srcs)
            raise Exception(mess)
        match = [p for p in self.projects if p.src == src]
        res = match[0]
        return res

    def add_project(self, src):
        """
        Add a project to a worktree
        :param src: path to the worktree, can be absolute,
            or relative to the worktree root

        """
        if os.path.isabs(src):
            src = os.path.relpath(src, self.root)
            src = qibuild.sh.to_posix_path(src)
        # Coming from user, can be an abspath:
        p_srcs = [p.src for p in self.projects]
        if src in p_srcs:
            mess  = "Project in %s already in worktree in %s" % (src, self.root)
            raise Exception(mess)

        project = Project()
        project.src = src
        root_elem = self.xml_tree.getroot()
        root_elem.append(project.xml_elem())
        self.dump()
        self.load()

    def __repr__(self):
        res = "<worktree in %s>" % self.root
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
        raise Exception("Could not find a work tree\n "
            "Here is what you can do :\n"
            " - try from a valid work tree\n"
            " - specify an existing work tree with \"--work-tree PATH\"\n"
            " - create a new work tree with \"qibuild init\"")
    if not os.path.exists(worktree):
        mess =  "Cannot open a worktree from %s\n" % worktree
        mess += "This path does not exist"
        raise Exception(mess)
    return WorkTree(worktree)


def guess_worktree():
    """Look for parent directories until a .qi dir is found somewhere.

    """
    head = os.getcwd()
    while True:
        d = os.path.join(head, ".qi")
        if os.path.isdir(d):
            return head
        (head, _tail) = os.path.split(head)
        if not _tail:
            break
    return None




def create(directory):
    """Create a new Qi work tree in the given directory

    """
    to_create = os.path.join(directory, ".qi")
    qibuild.sh.mkdir(to_create, recursive=True)
    qi_xml = os.path.join(directory, ".qi", "qibuild.xml")
    if not os.path.exists(qi_xml):
        with open(qi_xml, "w") as fp:
            fp.write("<qibuild />\n")
    return open_worktree(directory)


def project_path_from_cwd():
    """ Get the full path of a project using cwd

    """
    head = os.getcwd()
    qiproj_xml = None
    while True:
        qiproj_xml = os.path.join(head, "qiproject.xml")
        if os.path.exists(qiproj_xml):
            break
        (head, _tail) = os.path.split(head)
        if not _tail:
            break
    if not qiproj_xml:
        mess  = "Could not guess project name from current working directory\n"
        mess += "(No qiproject.xml found in the parent directories\n)"
        mess += "Please go inside a project, or specify the project name "
        mess += "from the command line"
    res = os.path.dirname(qiproj_xml)
    return res

def git_project_path_from_cwd():
    """ Get the path to the git repo of the current
    project using cwd

    """
    head = os.getcwd()
    res = None
    while True:
        if os.path.exists(os.path.join(head, ".git")):
            break
        (head, _tail) = os.path.split(head)
        if not _tail:
            return None
    return head

class Project:
    def __init__(self, src=None):
        self.src = src
        self.path = None
        self.git_project = None
        self.manifest = False

    def parse(self, xml_elem):
        self.src = xml_elem.get("src")
        self.git_project = xml_elem.get("git_project")
        self.manifest = qixml.parse_bool_attr(xml_elem, "manifest")

    def xml_elem(self):
        res = etree.Element("project")
        res.set("src", self.src)
        if self.git_project:
            res.set("git_project", self.git_project)
        if self.manifest:
            res.set("manifest", "true")
        return res

    def __repr__(self):
        res = "<Project in %s>" % (self.src)
        return res
