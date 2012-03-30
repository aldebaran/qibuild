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
            project.src = os.path.join(self.root, project.src)
            if os.path.exists(os.path.join(
                    project.src, ".git")):
                project.git_project = project
                self.git_projects.append(project)
            self.projects.append(project)
        self.git_projects.sort(key=operator.attrgetter("name"))
        self.projects.sort(key=operator.attrgetter("name"))


    def parse_git_projects(self):
        """ Iterate through every project.

        If project is a git directory, add it to the list.
        If not, look at the config and search of a matching project

        """
        projects_elem = self.xml_tree.findall("project")
        for project_elem in projects_elem:
            p_name = project_elem.get("name")
            git_name = project_elem.get("git_project")
            if git_name:
                project = self.get_project(p_name)
                git_project = self.get_project(git_name)
                project.git_project = git_project

    def parse_buildable_projects(self):
        """ Iterate through every project.

        If project contains a qirpoject.xml and a CMakeLists.txt
        file, add it to the list

        """
        for project in self.projects:
            src = project.src
            qiproj_xml = os.path.join(src, "qiproject.xml")
            cmake_lists = os.path.join(src, "CMakeLists.txt")
            if os.path.exists(qiproj_xml) and \
                os.path.exists(cmake_lists):
                self.buildable_projects.append(project)

    def get_project(self, name):
        """
        Get a project.
        :returns:  a :py:class:`Project` instance

        """
        p_names = [p.name for p in self.projects]
        if not name in p_names:
            mess  = "No such project: '%s'\n" % name
            mess += "Know projects are: %s" % ", ".join(p_names)
            raise Exception(mess)
        match = [p for p in self.projects if p.name == name]
        return match[0]

    def add_project(self, name, src=None):
        """
        Add a project to a worktree
        :param: name The name of the new project
        :param: path If not given, will be root/name

        """
        p_names = [p.name for p in self.projects]
        if name in p_names:
            project = self.get_project(name)
            mess  = "Cannot add project %s to worktree in %s\n" % (name, self.root)
            mess += "A project named %s already exists " % project.name
            mess += "(in %s)\n" % project.src
            mess += "Please choose a different name"
            raise Exception(mess)

        if not src:
            src = name
        project = Project()
        project.name = name
        project.src = src
        root_elem = self.xml_tree.getroot()
        root_elem.append(project.xml_elem())
        self.dump()
        self.load()


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


def project_from_cwd():
    """Return a project name from the current working directory

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
        mess += "(No qiproject.xml found in the parent directories\n"
        mess += "Please go inside a project, or specify the project name "
        mess += "from the command line"

    xml_elem = qixml.read(qiproj_xml)
    return xml_elem.getroot().get("name")


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



class Project:
    def __init__(self, name=None, src=None):
        self.name = name
        self.src = src
        self.git_project = None

    def parse(self, xml_elem):
        self.name = xml_elem.get("name")
        self.src = xml_elem.get("src")
        self.git_project = xml_elem.get("git_project")

    def xml_elem(self):
        res = etree.Element("project")
        res.set("name", self.name)
        res.set("src", self.src)
        if self.git_project:
            res.set("git_project", self.git_project)
        return res
