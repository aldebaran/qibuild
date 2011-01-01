##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##
import os
from qisrc import git

from qibuild.toc import guess_work_tree

__all__ = ( "git", "search_git_projects", "open", "create" )

def search_git_projects(directory=None):
    """ search for qibuild.manifest files recursively starting from directory
        this function return a list of directory.
    """
    result = list()
    #root is the only .git that could be recursive, feature or bug?
    if os.path.exists(os.path.join(directory, ".git")):
        #return (directory,)
        result.append(directory)
    for p in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, p)):
            result.extend(search_git_projects(os.path.join(directory, p)))
    return result

def create(work_tree):
    print "TODO: implement qisrc.create"
    pass

class Qis:
    def __init__(self, work_tree):
        self.work_tree    = work_tree
        self.git_projects = search_git_projects(work_tree)
        self.feed         = "qisrc.feed"

def open(work_tree, use_env=False):
    if not work_tree:
        work_tree = guess_work_tree(use_env)
    if not work_tree:
        work_tree = os.getcwd()
    if work_tree is None:
        raise Exception("Could not find current work tree, please go to a valid work tree.")
    return Qis(work_tree)
