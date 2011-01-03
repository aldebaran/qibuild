##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2011 Aldebaran Robotics
##

import os
import logging
from qitools.cmdparse    import default_parser
from qitools.configstore import ConfigStore

LOGGER = logging.getLogger("QiWorkTree")

def work_tree_parser(parser):
    """ Parser settings for every action using a toc dir
    """
    default_parser(parser)
    parser.add_argument("--work-tree", help="force work tree")


class QiWorkTree:
    """ This class represent a Qi worktree.
        - work_tree
        - configstore
        - buildable projects
        - git projects
    """

    def __init__(self, work_tree):
        self.work_tree          = work_tree
        self.configstore        = ConfigStore()
        self.buildable_projects = dict()
        self.git_projects       = dict()

        self._load_projects()
        self._load_configuration()

    def _load_projects(self):
        (git_p, src_p) = search_projects(self.work_tree)
        for d in src_p:
            self.buildable_projects[os.path.split(d)[-1]] = d
        for d in git_p:
            self.git_projects[os.path.split(d)[-1]] = d

    def _load_configuration(self):
        for name, ppath in self.buildable_projects.iteritems():
            self.configstore.read(os.path.join(ppath, "qibuild.manifest"))
        globalconfig = os.path.join(self.work_tree, ".qi", "build")
        if os.path.exists(globalconfig):
            self.configstore.read(globalconfig)
            LOGGER.debug("[Qi] worktree configuration:\n" + str(self.configstore))


def qiworktree_open(work_tree=None, use_env=False):
    """ open a qi worktree
        return a valid QiWorkTree instance
        TODO: explain why we search for manifest
    """
    if not work_tree:
        work_tree = guess_work_tree(use_env)
    if not work_tree:
        work_tree = search_manifest_directory(os.getcwd())
    if work_tree is None:
        raise Exception("Could not find toc work tree, please go to a valid work tree.")
    return QiWorkTree(work_tree)


def search_manifest_directory(working_directory):
    """ find the manifest associated to the working_directory, return None if not found """
    cwd     = os.path.normpath(os.path.abspath(working_directory))
    dirname = None

    #for each cwd parent folders, try to see if it match src
    while dirname or cwd:
        if (os.path.exists(os.path.join(cwd, "qibuild.manifest"))):
            return cwd
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            break
        cwd = new_cwd
    return None

def search_projects(directory=None, deep=3):
    """ search for qibuild.manifest files recursively starting from directory
        this function return a list of directory.
    """
    rgit = list()
    rsrc = list()
    if deep == 0:
        return (rgit, rsrc)

    if os.path.exists(os.path.join(directory, ".git")):
        rgit.append(directory)

    if os.path.exists(os.path.join(directory, "qibuild.manifest")):
        rsrc.append(directory)

    for p in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, p)):
            sub_rgit, sub_rsrc = search_projects(os.path.join(directory, p), deep - 1)
            rgit.extend(sub_rgit)
            rsrc.extend(sub_rsrc)
    return (rgit, rsrc)

def guess_work_tree(use_env=False):
    """Look for parent directories until a .toc dir is found somewhere.
    Otherwize, juste use TOC_WORK_TREE environnement
    variable
    """
    from_env = os.environ.get("QI_WORK_TREE")
    if use_env and from_env:
        return from_env
    head = os.getcwd()
    while True:
        d = os.path.join(head, ".qi")
        if os.path.isdir(d):
            return head
        (head, _tail) = os.path.split(head)
        if not _tail:
            break
    return None

# pylint: disable-msg=W0622,C0103
open = qiworktree_open
