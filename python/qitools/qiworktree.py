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
import qitools.sh

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
        self.user_config_path   = os.path.join(self.work_tree, ".qi", "build.cfg")

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
        if os.path.exists(self.user_config_path):
            self.configstore.read(self.user_config_path)
            LOGGER.debug("[Qi] worktree configuration:\n" + str(self.configstore))

    def update_config(self, section, name, key, value):
        """Update the .qi/build.cfg configuration file.

        for instance:

        update_config(
            foo, bar, spam, eggs
        )

        will write:
        [foo 'bar']
        spame = eggs

        """
        import ConfigParser
        parser = ConfigParser.ConfigParser()
        parser.read(self.user_config_path)
        section_name = '%s "%s"' % (section, name)
        if not parser.has_section(section_name):
            parser.add_section(section_name)
        if type(value) == type(""):
            parser.set(section_name, key, value)
        if type(value) == type([""]):
            parser.set(section_name, key, " ".join(value))
        with open(self.user_config_path, "w") as config_file:
            parser.write(config_file)

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

def search_projects(directory=None, depth=3):
    """ search for qibuild.manifest files recursively starting from directory
        this function return a list of directory.
    """
    rgit = list()
    rsrc = list()
    if depth == 0:
        return (rgit, rsrc)

    if os.path.exists(os.path.join(directory, ".git")):
        rgit.append(directory)

    if os.path.exists(os.path.join(directory, "qibuild.manifest")):
        rsrc.append(directory)

    for p in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, p)):
            sub_rgit, sub_rsrc = search_projects(os.path.join(directory, p), depth - 1)
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

def create(directory):
    """Create a new Qi worktree in the given directory

    """
    to_create = os.path.join(directory, ".qi")
    if os.path.exists(to_create):
        raise Exception("%s already exists!" % to_create)
    qitools.sh.mkdir(to_create, recursive=True)


def worktree_from_args(args):
    """Returns a suitable work tree from the command line
    """
    work_tree = None
    if args.work_tree:
        work_tree = args.work_tree
        work_tree = os.path.abspath(work_tree)
    elif os.environ.get("QI_WORK_TREE"):
        work_tree = os.environ["QI_WORK_TREE"]
        work_tree = os.path.abspath(work_tree)
    else:
        work_tree = os.getcwd()
    return work_tree


