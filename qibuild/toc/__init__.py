"""
Set of tools for aldebaran prog team.

"""

import os

from qibuild.toc           import dependencies
from qibuild.toc.bootstrap import bootstrap_project
from qibuild.toc.cmake     import configure_project
from qibuild.toc.make      import make_project
from qibuild.toc.toc       import Toc, get_projects_from_args

def _guess_work_tree(use_env=False):
    """Look for parent directories until a .toc dir is found somewhere.
    Otherwize, juste use TOC_WORK_TREE environnement
    variable
    """
    from_env = os.environ.get("TOC_WORK_TREE")
    if use_env and from_env:
        return from_env
    head = os.getcwd()
    while True:
        d = os.path.join(head, ".qibuild")
        if os.path.isdir(d):
            return head
        (head, _tail) = os.path.split(head)
        if not _tail:
            return None
    return None

def toc_open(worktree=None, toolchain_name=None, release=False, use_env=False):
    """ open a toc repository
    return a valid Toc instance
    """
    if not worktree:
        worktree = _guess_work_tree(use_env)
    if worktree is None:
        raise Exception("Could not find toc work tree, please go to a valid work tree.")
    return Toc(worktree, toolchain_name=None, release=False)

# def toc_create(work_tree, toc_dir=None):
#     """ create a toc repository
#     - check if everythink is okay
#     - open and return a Toc instance
#     """

#     if work_tree == None:
#         raise TocException("specify a valid work_tree")
#     if toc_dir == None:
#         toc_dir = os.path.join(work_tree, ".toc")

#     if os.path.isdir(toc_dir):
#         raise TocException("%s is already a toc repository" % toc_dir)
#     if not os.path.isdir(work_tree):
#         raise TocException("The TOC_WORK_TREE folder does not exists")
#     if os.path.isfile(toc_dir):
#         raise TocException("Fatal: a .toc file already exists")

#     #TODO: compare work_tree and toc_dir
#     os.mkdir(toc_dir)
#     fname = os.path.join(toc_dir, "base.cfg")
#     f = open(fname, "w")
#     f.write("""#Toc configuration file
# [general "toc"]
# src.folder = "."
# sdk.folder = sdk
# ## Uncomment this to build in debug by default
# # build.config = debug

# ## Uncomment to build with special flags
# ## value must be a [build] section, see below
# # build.config = lite


# ## Note:
# # build.config = lite.debug also works :)

# [build "lite"]
# cmake.flags = "WITH_NAOQI_MODULES=OFF WITH_QT=OFF"
# """)
#     f.close()

