import qisys.parsers
import qilinguist.builder

from qilinguist.worktree import LinguistWorkTree, new_linguist_project
import qilinguist.builder

def get_linguist_worktree(args):
    worktree = qisys.parsers.get_worktree(args)
    return LinguistWorkTree(worktree)

def get_linguist_projects(worktree, args, default_all=False):
    parser = LinguistProjectParser(worktree)
    return parser.parse_args(args, default_all=default_all)

def get_linguist_builder(args):
    worktree = get_linguist_worktree(args)
    projects = get_linguist_projects(worktree, args)
    builder = qilinguist.builder.QiLinguistBuilder(worktree)
    builder.projects = projects
    return builder




##
# Implementation details

class LinguistProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a LinguistWorkTree """

    def __init__(self, linguist_worktree):
        self.linguist_worktree = linguist_worktree
        self.linguist_projects = linguist_worktree.linguist_projects

    def all_projects(self, args):
        return self.linguist_projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        matches the current directory

        """
        worktree = self.linguist_worktree.worktree
        parser = qisys.parsers.WorkTreeProjectParser(worktree)
        worktree_projects = parser.parse_no_project(args)
        if not worktree_projects:
            raise CouldNotGuessProjectName()

        # WorkTreeProjectParser returns None or a list of one element
        worktree_project = worktree_projects[0]
        linguist_project = new_linguist_project(self.linguist_worktree,
                                                worktree_project)
        if not linguist_project:
            raise CouldNotGuessProjectName()

        return self.parse_one_project(args, linguist_project.name)

    def parse_one_project(self, args, project_arg):
        """ Get one linguist project given its name """

        project = self.linguist_worktree.get_linguist_project(project_arg,
                                                              raises=True)
        return [project]

class CouldNotGuessProjectName(Exception):
    def __str__(self):
        return """
Could not guess linguist project name from current working directory
Please go inside a translatable project, or specify the project name
on the command line
"""

