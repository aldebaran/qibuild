import qisys.parsers

from qidoc.worktree import DocWorkTree, new_doc_project

def get_doc_worktree(args):
    worktree = qisys.parsers.get_worktree(args)
    return DocWorkTree(worktree)


def get_doc_worktree(doc_worktree, args, default_all=False):
    parser = DocProjectParser(doc_worktree)
    return parser.parse_args(args, default_all=default_all)

##
# Implementation details

class DocProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a DocWorkTree """

    def __init__(self, doc_worktree):
        self.doc_worktree = doc_worktree
        self.doc_projects = doc_worktree.doc_projects

    def all_projects(self, args):
        return self.doc_projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        matches the current directory

        """
        worktree = self.doc_worktree.worktree
        parser = qisys.parsers.WorkTreeProjectParser(worktree)
        worktree_projects = parser.parse_no_project(args)
        if not worktree_projects:
            raise CouldNotGuessProjectName()

        # WorkTreeProjectParser returns None or a list of one element
        worktree_project = worktree_projects[0]
        doc_project = new_doc_project(self.doc_worktree, worktree_project)
        if not doc_project:
            raise CouldNotGuessProjectName()

        return self.parse_one_project(args, doc_project.name)

    def parse_one_project(self, args, project_arg):
        """ Get one doc project given its name """

        project = self.doc_worktree.get_doc_project(project_arg, raises=True)
        return [project]

class CouldNotGuessProjectName(Exception):
    def __str__(self):
        return """
Could not guess doc project name from current working directory
Please go inside a translatable project, or specify the project name
on the command line
"""

