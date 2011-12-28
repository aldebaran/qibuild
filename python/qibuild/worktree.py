## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""This package contains the WorkTree object.

Typical usage is:

 - Create a new worktree.

This create /path/to/work/.qi,

 - Go to /path/to/work/src/foo, find the "bar" project

Explore each parent directory until a ".qi" is found.
Use the parent directory as a work tree.
Build a WorkTree object from the work tree.
Parses the worktree so that WorkTree every buildable projects
(directories that contains a qibuild.manifest)

To find the "bar" project, look for a project named "bar" in
worktree.projects

Note: the .qi also contains a config file, so you can
have different configurations with different work trees if you need.

"""

import os
import logging
from qibuild.cmdparse    import default_parser
import qibuild.sh

LOGGER = logging.getLogger("WorkTree")

class WorkTreeException(Exception):
    """Custom exception """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message

class ProjectAlreadyExists(Exception):
    """Just a custom exception """
    def __init__(self, url, name, path):
        self.url = url
        self.name = name
        self.path = path

    def __str__(self):
        message = "Error when adding project %s (%s)\n" % (self.url, self.name)
        message += "%s already exists." % self.path
        return message


def work_tree_parser(parser):
    """ Parser settings for every action using a work tree.
    """
    default_parser(parser)
    parser.add_argument("--work-tree", help="Use a specific work tree path.")


class WorkTree:
    """ This class represent a Qi worktree.
        - work_tree
        - buildable projects
        - git projects
    """

    def __init__(self, work_tree, path_hints=None):
        self.work_tree          = work_tree

        self.buildable_projects = dict()
        self.git_projects       = dict()

        if not path_hints:
            path_hints = list()
        if self.work_tree not in path_hints:
            path_hints.append(self.work_tree)
        self._load_projects(path_hints)

    def _load_projects(self, path_hints):
        """ Parse a worktree.

        Look for git projects and qibuild projects (directories containing a
        qibuild.manifest and update self.buildable_projects and self.git_projects

        Make sure there is no name conflict.
        """
        for p in path_hints:
            (git_p, src_p) = search_projects(p)
            for d in src_p:
                # Get the name of the project from its directory:
                project_name = qibuild.project.name_from_directory(d)
                pdir = self.buildable_projects.get(project_name)
                #project already exist
                if pdir:
                    if qibuild.sh.to_native_path(d) != qibuild.sh.to_native_path(pdir):
                        mess  = "Name conflict: those two projects:\n"
                        mess += "\t\t%s\n\t\tand\n\t\t%s\n" % (d, pdir)
                        mess += "have the same name. (%s)\n" % project_name
                        mess += "Please change the name in the qibuild.manifest, "
                        mess += "or move one of them outside you worktree."
                        raise WorkTreeException(mess)
                else:
                    self.buildable_projects[project_name] = d
# FIXME:
# If you have something like
# | worktree
#   |__ .qi
#   |__ bar
#       |__ .git
#   |__foo
#      |__ bar
#          |__ .git
# the load with fail because we store paths to git projects
# using the basename of the directory.
# An easy way to prevent this from happenning would be
# to use relative paths to the worktree as keys.
# But, the behavior of qisrc would be too much different
# from the one of qibuild, so maybe this is not such
# a good idea...
            for d in git_p:
                conflicting_path = self.git_projects.get(os.path.basename(d))
                if conflicting_path:
                    if qibuild.sh.to_native_path(d) != qibuild.sh.to_native_path(conflicting_path):
                        mess  = "Name conflict: these git source trees:\n"
                        mess += "\t\t%s\n\t\tand\n\t\t%s\n" % (d, conflicting_path)
                        mess += "have the same basename.\n"
                        mess += "Please rename one of them, or move one of then outside your worktree"
                        raise WorkTreeException(mess)
                else:
                    self.git_projects[os.path.basename(d)] = d


def worktree_open(work_tree=None):
    """ Open a qi worktree.

        Return a valid WorkTree instance.

        The WorkTree instance will have the following important members
        initialized:
         qiwt.buildable_projects  : a list of Project instances
         qiwt.git_projects        : al list of git repositories

        If worktree is None, guess it from the current working dir.
    """
    path_hints = list()
    if not work_tree:
        work_tree = guess_work_tree()
        LOGGER.debug("found a qi worktree: %s", work_tree)
    current_project = search_current_project_root(os.getcwd())
    if not work_tree:
        # Sometimes we you just want to create a fake worktree object because
        # you just want to build one project (no dependencies at all, no configuration...)
        # In this case, just searching for a manifest from the current working directory
        # is enough
        work_tree = current_project
        LOGGER.debug("no work tree found using the project root: %s", work_tree)

    if current_project:
        # Add the current project has a hint.
        #
        # We use path_hints because we guess_work_tree from the cwd.
        # There is no limit for how fare we look for the worktree directory,
        # so there could be there could be 4 or more #
        # folder separating cwd from work_tree, and in this case the current
        # project will not be found.
        # (when building the WorkTree object, we only seach for projects)
        # in the first 4 levels of folders starting from work_tree.

        # Tldr: this solves a quite a nasty bug when you have:
        # worktree/.qi/a/b/c/d/e/f/project, and you run qibuild commands from
        # the <project> directory.
        path_hints.append(current_project)

    if work_tree is None:
        raise WorkTreeException("Could not find a work tree\n "
            "Here is what you can do :\n"
            " - try from a valid work tree\n"
            " - specify an existing work tree with \"--work-tree PATH\"\n"
            " - create a new work tree with \"qibuild init\"")
    return WorkTree(work_tree, path_hints=path_hints)

def search_current_project_root(working_directory):
    """ When you run qibuild without any arguement,
    we try to guess the current project using the current working dir.

    Two cases:
        - inside a subdir of qibuild project: look for a qibuild.manifest
        - inside the build directory of a qibuild project: search a
        cmake build directory, and guess the project from the contents
        of the cmake cache.
    """
    cwd = _search_manifest_directory(working_directory)
    if not cwd:
        #get the project directory associated to the build dir
        tmp = _search_build_directory(working_directory)
        if not tmp:
            return None
        #verify it's really a project dir
        cwd = _search_manifest_directory(tmp)
    return cwd

def _search_build_directory(working_directory):
    """ find the manifest associated to the working_directory, return None if not found """
    cwd     = os.path.normpath(os.path.abspath(working_directory))
    dirname = None

    #for each cwd parent folders, try to see if it match src
    while dirname or cwd:
        if os.path.exists(os.path.join(cwd, "CMakeCache.txt")):
            with open(os.path.join(cwd, "CMakeCache.txt"), "r") as f:
                lines = f.readlines()
                for l in lines:
                    if l.startswith("CMAKE_HOME_DIRECTORY:INTERNAL="):
                        return str(l[30:]).strip()
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            break
        cwd = new_cwd
    return None

def _search_manifest_directory(working_directory):
    """ find the manifest associated to the working_directory, return None if not found """
    cwd     = os.path.normpath(os.path.abspath(working_directory))
    dirname = None

    #for each cwd parent folders, try to see if it match src
    while dirname or cwd:
        if os.path.exists(os.path.join(cwd, "qibuild.manifest")):
            return cwd
        if os.path.exists(os.path.join(cwd, "manifest.xml")):
            return cwd
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            break
        cwd = new_cwd
    return None

def search_projects(directory=None, depth=4):
    """ Search for qibuild.manifest files recursively starting from directory
        This function return a list of directories.
    """
    # TODO: caching, please!
    # TODO: may warn the user that this may take some time, of force user
    # to run qibuild init in empty directories
    rgit = list()
    rsrc = list()
    if depth == 0:
        return (rgit, rsrc)

    if os.path.exists(os.path.join(directory, ".git")):
        rgit.append(directory)

    if os.path.exists(os.path.join(directory, "qibuild.manifest")):
        rsrc.append(directory)

    if os.path.exists(os.path.join(directory, "manifest.xml")):
        rsrc.append(directory)

    blacklist_file = os.path.join(directory, ".qiblacklist")
    if os.path.exists(blacklist_file):
        return(rgit, rsrc)

    subdirs = list()
    try:
        dir_contents = [os.path.join(directory, s) for s in os.listdir(directory)]
        subdirs = [s for s in dir_contents if os.path.isdir(s)]
    except OSError:
        pass
    # If os.listdir fails (permission denied for instance),
    # we will iter on a empty list, so no worry :)
    for p in subdirs:
        sub_rgit, sub_rsrc = search_projects(p, depth - 1)
        rgit.extend(sub_rgit)
        rsrc.extend(sub_rsrc)
    return (rgit, rsrc)

def guess_work_tree():
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


