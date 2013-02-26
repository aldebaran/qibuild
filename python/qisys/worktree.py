## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the WorkTree object.

"""

import os
import qisys.log
import operator

from qisys import ui
import qisys.command
import qisys.sh
import qisys.qixml
from qisys.qixml import etree


class WorkTreeError(Exception):
    """ Just a custom exception. """

class NotInWorkTree(Exception):
    """ Just a custom exception. """
    def __str__(self):
        return """ Could not guess worktree from current working directory
  Here is what you can do :
     - try from a valid work tree
     - specify an existing work tree with --work-tree PATH
     - create a new work tree with `qibuild init`
"""

class WorkTree(object):
    """ This class represent a :term:`worktree`. """
    def __init__(self, root, sanity_check=True):
        """
        Construct a new worktree

        :param root: The root directory of the worktree.
        :param allow_nested: Allow nested worktrees.

        """
        self.root = root
        self.projects = list()
        self.load()
        if sanity_check:
            self.check()

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
        self.check()

    def check(self):
        """ Perform a few sanity checks """
        # Check that we are not in a git project:
        import qisrc.git
        git_root = qisrc.git.get_repo_root(self.root)
        if git_root:
            raise WorkTreeError(""" Found a .qi inside a git project"
git project: {0}
worktree root: {1}
""".format(git_root, self.root))

        # Check that we are not in an other worktree:
        parent_worktree = guess_worktree(self.root)
        if parent_worktree and parent_worktree != self.root:
            raise WorkTreeError("""{0} is already in a worktee
(in {1})
""".format(self.root, parent_worktree))

        non_existing = list()
        # Check that every source exists
        for project in self.projects:
            if not os.path.exists(project.path):
                non_existing.append(project)

        if not non_existing:
            return

        mess = ["The following projects:\n"]
        for project  in non_existing:
            mess.extend([ui.green, " *", ui.blue, project.src, "\n"])
        mess.extend([ui.reset, ui.brown])
        mess.append("are registered in the worktree, but their paths no longer exists.")
        ui.warning(*mess)
        answer = qisys.interact.ask_yes_no("Do you want to remove them", default=True)
        if not answer:
            return
        for project  in non_existing:
            ui.info(ui.green, "Removing", ui.reset, project.src)
            self.remove_project(project.path)

    @property
    def dot_qi(self):
        """Get the dot_qi directory."""
        return os.path.join(self.root, ".qi")

    @property
    def worktree_xml(self):
        """Get the path to .qi/worktree.xml """
        return os.path.join(self.dot_qi, "worktree.xml")

    @property
    def qibuild_xml(self):
        """Get the path to .qi/qibuild.xml """
        # XXX: This should be in BuildWorktree, but then
        # we have a coupling between BuildWorktree and GitWorkTree ....
        return os.path.join(self.dot_qi, "qibuild.xml")


        """ Get the qibuild.xml path """
        # qisrc needs that when it syncs build profiles,
        # and the relationships between qisrc and qibuild are not
        # obvious for now ...
        return os.path.join(self.dot_qi, "qibuild.xml")

    def has_project(self, src):
        srcs = (p.src.lower() for p in self.projects)
        return src.lower() in srcs

    def dump(self):
        """ Dump self to the worktree.xml file. """
        qisys.sh.mkdir(self.dot_qi, recursive=True)
        qisys.qixml.write(self.xml_tree, self.worktree_xml)

    def parse_projects(self):
        """ Parse .qi/worktree.xml, resolve subprojects. """
        projects_elem = self.xml_tree.findall("project")
        for project_elem in projects_elem:
            project = WorkTreeProject(self)
            parser = ProjectParser(project)
            parser.parse(project_elem)
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
        for sub_project_src in project.subprojects:
            src = os.path.join(project.src, sub_project_src)
            src = qisys.sh.to_posix_path(src)
            sub_project = WorkTreeProject(self, src=src)
            sub_project.parse_qiproject_xml()
            res.append(sub_project)
            self._rec_parse_sub_projects(sub_project, res)

    def get_project(self, src, raises=False):
        """ Get a project

        :param src: a absolute path, or a path relative to the worktree
        :param raises: Raises if project is not found
        :returns:  a :py:class:`WorkTreeProject` instance or None if raises is
            False and project is not found

        """
        src = self.normalize_path(src)
        if not self.has_project(src):
            if not raises:
                return None
            mess  = "No project in '%s'\n" % src
            mess += "Known projects are in %s" % ", ".join([p.src for p in self.projects])
            raise WorkTreeError(mess)
        match = [p for p in self.projects if p.src == src]
        res = match[0]
        return res

    def add_project(self, src):
        """ Add a project to a worktree

        :param src: path to the project, can be absolute,
                    or relative to the worktree root

        """
        # Coming from user, can be an abspath:
        src = self.normalize_path(src)
        if self.has_project(src):
            mess  = "Could not add project to worktree\n"
            mess += "Path %s is already registered\n" % src
            mess += "Current worktree: %s" % self.root
            raise WorkTreeError(mess)

        project = WorkTreeProject(self, src=src)
        parser = ProjectParser(project)
        root_elem = self.xml_tree.getroot()
        root_elem.append(parser.xml_elem())
        self.dump()
        self.load()

    def remove_project(self, src, from_disk=False):
        """ Remove a project from a worktree

        :param src: path to the project, can be absolute,
                    or relative to the worktree root
        :param from_disk: also erase project files from disk


        """
        src = self.normalize_path(src)
        if not self.has_project(src):
            raise WorkTreeError("No such project: %s" % src)
        root_elem = self.xml_tree.getroot()
        for project_elem in root_elem.findall("project"):
            if project_elem.get("src") == src:
                if from_disk:
                    to_remove = self.get_project(src).path
                    qisys.sh.rm(to_remove)
                root_elem.remove(project_elem)
        self.dump()
        self.load()

    def normalize_path(self, path):
        """ Make sure the path is a POSIX path, relative to
        the worktree root

        """
        if os.path.isabs(path):
            path = os.path.relpath(path, start=self.root)
        path = path.replace(ntpath.sep, posixpath.sep)
        path = os.path.normcase(path)
        return path

    def __repr__(self):
        res  = "<WorkTree in %s\n" % self.root
        res += repr_list_projects(self.projects)
        res += ">\n"
        return res


def open_worktree(root):
    """ Open a qi worktree.

    :return: a valid :py:class:`WorkTree` instance.

    """
    if not os.path.exists(root):
        mess =  "Cannot open a worktree from %s\n" % root
        mess += "This path does not exist"
        raise WorkTreeError(mess)
    res = WorkTree(root)
    return res


def create(directory, force=False):
    """Create a new Qi work tree in the given directory.

    If already in a worktre, will do nothing, unless
    force is True, and then will re-initialize the worktree.

    """
    dot_qi = os.path.join(directory, ".qi")
    qisys.sh.mkdir(dot_qi, recursive=True)
    qi_xml = os.path.join(dot_qi, "qibuild.xml")
    if not os.path.exists(qi_xml) or force:
        with open(qi_xml, "w") as fp:
            fp.write("<qibuild />\n")
    return open_worktree(directory)


class WorkTreeProject(object):
    def __init__(self, worktree, src=None):
        self.worktree = worktree
        self.src = src
        self.subprojects = list()

    @property
    def path(self):
        """Give the path in native form."""
        path = os.path.join(self.worktree.root, self.src)
        return qisys.sh.to_native_path(path)

    @property
    def qiproject_xml(self):
        """Give the path to the qiproject.xml."""
        return os.path.join(self.path, "qiproject.xml")

    def parse_qiproject_xml(self):
        if not os.path.exists(self.qiproject_xml):
            return
        tree = qisys.qixml.read(self.qiproject_xml)
        project_elems = tree.findall("project")
        for project_elem in project_elems:
            sub_src = qisys.qixml.parse_required_attr(project_elem, "src",
                                                xml_path=self.qiproject_xml)
            full_path = os.path.join(self.path, sub_src)
            if not os.path.exists(full_path):
                raise WorkTreeError(""" \
Invalid qiproject.xml detected (in {0})
Found an invalid sub project: {1}
{2} does not exits
""".format(self.qiproject_xml, sub_src, full_path))
            self.subprojects.append(sub_src)


class ProjectParser(qisys.qixml.XMLParser):
    def __init__(self, target):
        super(ProjectParser, self).__init__(target)

    def _post_parse_attributes(self):
        self.check_needed("src")

    def xml_elem(self):
        res = etree.Element("project")
        res.set("src", self.target.src)
        return res


def repr_list_projects(projects, name = "projects"):
    res = ""
    if len(projects):
        res += name
        for i, project in enumerate(projects):
            res += "(%s) %s, " % (i, project.src)
        res += "\n"
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
        raise NotInWorkTree()
    else:
        return None


