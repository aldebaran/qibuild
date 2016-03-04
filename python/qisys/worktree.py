## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""This package contains the WorkTree object.

"""

import abc
import locale
import os
import ntpath
import posixpath
import operator
import difflib

import qisys.error
import qisys.project
import qisys.command
import qisys.sh
import qisys.qixml
from qisys import ui

import qibuild.config


class WorkTree(object):
    """ This class represent a :term:`worktree`. """
    def __init__(self, root, sanity_check=True):
        """
        Construct a new worktree

        :param root: The root directory of the worktree.
        :param allow_nested: Allow nested worktrees.

        """
        if not os.path.exists(root):
            raise qisys.error.Error(""" \
Could not open WorkTree in {0}.
This path does not exist
""".format(root))

        self._observers = list()
        self.root = root
        self.cache = self.load_cache()
        # Re-parse every qiproject.xml to visit the subprojects
        self.projects = list()
        self.load_projects()
        if sanity_check:
            self.check()
        self.register_self()

    def register_self(self):
        """ Register to the global list of all worktrees  in
        ~/.config/qi/qibuild.xml

        """
        qibuild_cfg = qibuild.config.QiBuildConfig()
        to_read = qibuild.config.get_global_cfg_path()
        qibuild_cfg.read(to_read, create_if_missing=True)
        encoding = locale.getpreferredencoding()
        as_unicode = self.root.decode(encoding)
        qibuild_cfg.add_worktree(as_unicode)
        qibuild_cfg.write()

    def register(self, observer):
        """ Called when an observer wants to be notified
        about project changes

        """
        self._observers.append(observer)

    def load_cache(self):
        """ Load the worktree.xml file. """
        self.projects = list()
        if not os.path.exists(self.worktree_xml):
            qisys.sh.mkdir(self.dot_qi)
            with open(self.worktree_xml, "w") as fp:
                fp.write("<worktree />\n")
        cache = WorkTreeCache(self.worktree_xml)
        # Remove non-existing sources
        for src in cache.get_srcs():
            if not os.path.exists(os.path.join(self.root, src)):
                cache.remove_src(src)
        return cache

    def reload(self):
        """ Re-read every qiproject.xml.
        Useful when projects are added or removed, or when
        qiproject.xml change

        """
        self.cache = self.load_cache()
        self.load_projects()
        for observer in self._observers:
            observer.reload()

    def check(self):
        """ Perform a few sanity checks """
        # Check that we are not in an other worktree:
        parent_worktree = guess_worktree(os.path.join(self.root, ".."))
        if parent_worktree and parent_worktree != self.root:
            ui.warning("""Nested worktrees detected:
{0} is already in a worktree
(in {1})
""".format(self.root, parent_worktree))

    @property
    def dot_qi(self):
        """Get the dot_qi directory."""
        res = os.path.join(self.root, ".qi")
        qisys.sh.mkdir(res)
        return res

    @property
    def worktree_xml(self):
        """Get the path to .qi/worktree.xml """
        worktree_xml = os.path.join(self.dot_qi, "worktree.xml")
        if not os.path.exists(worktree_xml):
            with open(worktree_xml, "w") as fp:
                fp.write("<worktree />")
        return worktree_xml

    def has_project(self, path):
        src = self.normalize_path(path)
        srcs = (p.src for p in self.projects)
        return src in srcs

    def load_projects(self):
        """ For every project in cache, re-read the subprojects and
        and them to the list

        """
        self.projects = list()
        srcs = self.cache.get_srcs()
        for src in srcs:
            project = qisys.project.WorkTreeProject(self, src)
            project.parse_qiproject_xml()
            self.projects.append(project)

        res = set(self.projects)
        for project in self.projects:
            self._rec_parse_sub_projects(project, res)
        self.projects = sorted(res, key=operator.attrgetter("src"))

    def _rec_parse_sub_projects(self, project, res):
        """ Recursively parse every project and subproject,
        filling up the res list.

        """
        for sub_project_src in project.subprojects:
            src = os.path.join(project.src, sub_project_src)
            src = qisys.sh.to_posix_path(src)
            sub_project = qisys.project.WorkTreeProject(self, src)
            sub_project.parse_qiproject_xml()
            res.add(sub_project)
            self._rec_parse_sub_projects(sub_project, res)

    def get_project(self, src, raises=False):
        """ Get a project

        :param src: a absolute path, or a path relative to the worktree
        :param raises: Raises if project is not found
        :returns:  a :py:class:`.WorkTreeProject` instance or None if raises is
            False and project is not found

        """
        src = self.normalize_path(src)
        if not self.has_project(src):
            if not raises:
                return None
            mess  = ui.did_you_mean("No project in '%s'\n" % src,
                                    src, [x.src for x in self.projects])
            raise WorkTreeError(mess)
        match = (p for p in self.projects if p.src == src)
        return match.next()

    def add_project(self, path):
        """ Add a project to a worktree

        :param path: path to the project, can be absolute,
                    or relative to the worktree root

        """
        src = self.normalize_path(path)
        if self.has_project(src):
            mess  = "Could not add project to worktree\n"
            mess += "Path %s is already registered\n" % src
            mess += "Current worktree: %s" % self.root
            raise WorkTreeError(mess)
        self.cache.add_src(src)
        self.load_projects()
        project = self.get_project(src)
        for observer in self._observers:
            observer.reload()
        return project

    def remove_project(self, path, from_disk=False):
        """ Remove a project from a worktree

        :param path: path to the project, can be absolute,
                    or relative to the worktree root
        :param from_disk: also erase project files from disk

        """
        src = self.normalize_path(path)
        if not self.has_project(src):
            raise WorkTreeError("No such project: %s" % src)
        project = self.get_project(src)
        if from_disk:
            qisys.sh.rm(project.path)
        self.cache.remove_src(src)
        self.load_projects()
        for observer in self._observers:
            observer.reload()

    def move_project(self, path, new_path):
        """ Move a project from a worktree """
        src = self.normalize_path(path)
        new_src = self.normalize_path(new_path)
        if not self.has_project(src):
            raise WorkTreeError("No such project: %s" % src)
        if self.has_project(new_src):
            mess  = "Could not move project\n"
            mess += "Path %s is already registered\n" % src
            mess += "Current worktree: %s" % self.root
        self.cache.remove_src(src)
        self.cache.add_src(new_src)
        self.load_projects()
        project = self.get_project(src)
        for observer in self._observers:
            observer.reload()

    def normalize_path(self, path):
        """ Make sure the path is a POSIX path, relative to
        the worktree root

        """
        if os.path.isabs(path):
            path = os.path.relpath(path, start=self.root)
        path = path.replace(ntpath.sep, posixpath.sep)
        if os.name == 'nt':
            path = path.lower()
        return path

    def __repr__(self):
        res  = "<WorkTree in %s\n" % self.root
        res += repr_list_projects(self.projects)
        res += ">\n"
        return res


def repr_list_projects(projects, name = "projects"):
    res = ""
    if projects:
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
        try:
            cwd = os.getcwd()
        except OSError as e:
            raise qisys.error.Error("Working directory is not an existing directory")
    cwd = qisys.sh.to_native_path(cwd)
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

class WorkTreeObserver(object):
    """ To be subclasses for objects willing to be
    notified when a project is added or removed from
    the worktree

    """
    __metaclass__ = abc.ABCMeta

    @abc.abstractmethod
    def reload(self):
        pass

class WorkTreeCache(object):
    """ Cache the paths to all the projects registered
    in a worktree

    """
    def __init__(self, xml_path):
        self.xml_path = xml_path
        self.xml_root = qisys.qixml.read(xml_path).getroot()

    def add_src(self, src):
        """ Add a new source to the cache """
        project_elem = qisys.qixml.etree.Element("project")
        project_elem.set("src", src)
        self.xml_root.append(project_elem)
        qisys.qixml.write(self.xml_root, self.xml_path)

    def remove_src(self, src):
        """ Remove one source from the cache """
        projects_elem = self.xml_root.findall("project")
        for project_elem in projects_elem:
            if project_elem.get("src") == src:
                self.xml_root.remove(project_elem)
        qisys.qixml.write(self.xml_root, self.xml_path)

    def get_srcs(self):
        """ Get all the sources registered in the cache """
        srcs = list()
        projects_elem = self.xml_root.findall("project")
        for project_elem in projects_elem:
            srcs.append(qisys.qixml.parse_required_attr(project_elem, "src"))
        return srcs

class WorkTreeError(qisys.error.Error):
    """ Just a custom exception. """

class NotInWorkTree(qisys.error.Error):
    """ Just a custom exception. """
    def __str__(self):
        return """ Could not guess worktree from current working directory
  Here is what you can do :
     - try from a valid work tree
     - specify an existing work tree with --work-tree PATH
     - create a new work tree with `qibuild init`
"""

class NoSuchProject(qisys.error.Error):
    def __init__(self, name, message):
        self.name = name
        self.message = message

    def __str__(self):
        return self.message
