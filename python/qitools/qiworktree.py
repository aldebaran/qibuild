## Copyright (C) 2011 Aldebaran Robotics

"""This package contains the QiWorkTree object.

Typical usage is:

 - Create a new worktree.

This create /path/to/work/.qi,

 - Go to /path/to/work/src/foo, find the "bar" project

Explore each parent directory until a ".qi" is found.
Use the parent directory as a work tree.
Build a QiWorkTree object from the work tree.
Parses the worktree so that QiWorkTree every buildable projects
(directories that contains a qibuild.manifest)

To find the "bar" project, look for a project named "bar" in
qiworktree.projects

Note: the .qi also contains a config file, so you can
have different configurations with different work trees if you need.

"""

import os
import logging
from qitools.cmdparse    import default_parser
from qitools.configstore import ConfigStore
import qitools.sh

LOGGER = logging.getLogger("QiWorkTree")

class WorkTreeException(Exception):
    """Custom exception """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def work_tree_parser(parser):
    """ Parser settings for every action using a work tree.
    """
    default_parser(parser)
    parser.add_argument("--work-tree", help="Use a specific work tree path.")


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
            # Get the name of the project from its directory:
            project_name = project_name_from_directory(d)
            if self.buildable_projects.get(project_name):
                raise WorkTreeException("Conflict: two projects have the same name '%s': %s and %s"
                                        % (project_name, self.buildable_projects.get(project_name), d))
            self.buildable_projects[project_name] = d
        for d in git_p:
            self.git_projects[os.path.basename(d)] = d

    def _load_configuration(self):
        for name, ppath in self.buildable_projects.iteritems():
            self.configstore.read(os.path.join(ppath, "qibuild.manifest"))
        if os.path.exists(self.user_config_path):
            self.configstore.read(self.user_config_path)
            LOGGER.debug("[Qi] worktree configuration:\n" + str(self.configstore))

def qiworktree_open(work_tree=None, use_env=False):
    """ open a qi worktree
        return a valid QiWorkTree instance
    """
    if not work_tree:
        work_tree = guess_work_tree(use_env)
        LOGGER.debug("found a qi worktree: %s", work_tree)
    if not work_tree:
        # Sometimes we you just want to create a fake worktree object because
        # you just want to build one project (no dependencies at all, no configuration...)
        # In this case, just searching for a manifest from the current working directory
        # is enough
        work_tree = search_manifest_directory(os.getcwd())
        LOGGER.debug("no work tree found using the project root: %s", work_tree)
    if work_tree is None:
        raise WorkTreeException("Could not find a work tree\n "
            "Here is what you can do :\n"
            " - try from a valid work tree\n"
            " - specify an existing work tree with \"--work-tree PATH\"\n"
            " - create a new work tree with \"qibuild init\"")
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
    """ Search for qibuild.manifest files recursively starting from directory
        This function return a list of directories.
    """
    # TODO: caching, please!
    # TODO: may warn the user that this may take some times, of force user
    # to run qibuild init in empty directories
    rgit = list()
    rsrc = list()
    if depth == 0:
        return (rgit, rsrc)

    if os.path.exists(os.path.join(directory, ".git")):
        rgit.append(directory)

    if os.path.exists(os.path.join(directory, "qibuild.manifest")):
        rsrc.append(directory)

    subdirs = list()
    try:
        subdirs = os.listdir(directory)
    except OSError:
        pass
    for p in subdirs:
        if os.path.isdir(os.path.join(directory, p)):
            sub_rgit, sub_rsrc = search_projects(os.path.join(directory, p), depth - 1)
            rgit.extend(sub_rgit)
            rsrc.extend(sub_rsrc)
    return (rgit, rsrc)

def guess_work_tree(use_env=False):
    """Look for parent directories until a .qi dir is found somewhere.
    Otherwise, just use TOC_WORK_TREE environment
    variable
    """
    # FIXME: not sure who would need use_env to be False ...
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


def project_name_from_directory(project_dir):
    """Get the project name from the project directory

    The directory should contain a "qibuild.manifest" file,
    looking like

        [project foo]
        ...

    If such a section can not be found, raise an exception
    """
    config = qitools.configstore.ConfigStore()
    conf_file = os.path.join(project_dir, "qibuild.manifest")
    config.read(conf_file)
    project_names = config.get("project", default=dict()).keys()
    if len(project_names) != 1:
        mess  = "The file %s is invalid\n" % conf_file
        mess += "It should contains exactly one project section"
        raise Exception(mess)

    return project_names[0]


def create(directory):
    """Create a new Qi work tree in the given directory

    """
    to_create = os.path.join(directory, ".qi")
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


