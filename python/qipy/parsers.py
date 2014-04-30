import qisys.parsers
import qipy.worktree

def get_python_worktree(args):
    worktree = qisys.parsers.get_worktree()
    python_worktree = qipy.worktree.PythonWorkTree(worktree)
    return python_worktree

class DocProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a PythonWorkTree """

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

