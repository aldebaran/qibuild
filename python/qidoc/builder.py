import os

from qisys import ui
import qisys.sort


class DocBuilder(object):
    """ Build and install doc projects.

    Initialize with a `base_project`, which will
    be at the root of the dest dir when installed.

    The `install` step is required to have redistributable
    documentation folder, while you can browse the documentation
    directly from the build dir.

    """
    def __init__(self, doc_worktree):
        self.doc_worktree = doc_worktree
        self.single = False
        self.deps_solver = None
        self.base_project = None
        self.version = "latest"
        self.hosted = True
        self.debug = True
        self.werror = False

    def configure(self):
        """ Configure the projects in the right order

        """
        projects = self.get_dep_projects()
        configure_args = {
            "version" : self.version,
            "hosted"  : self.hosted,
            "debug"   : self.debug,
        }
        for project in projects:
            project.configure(**configure_args)

    def build(self):
        """ Build the projects in the right order,
        making sure they are configured first

        """
        projects = self.get_dep_projects()
        for i, project in enumerate(projects):
            ui.info_count(i, len(projects),
                          ui.green, "Building", ui.blue, project.name)
            project.build(werror=self.werror)

    def install(self, destdir):
        """ Install the doc projects to a dest dir

        """
        projects = self.get_dep_projects()
        for i, project in enumerate(projects):
            if i == len(projects) - 1:
                real_dest = destdir
            else:
                real_dest = os.path.join(destdir, project.dest)
            project.dest = real_dest
            ui.info_count(i, len(projects),
                          ui.green, "Installing",
                          ui.blue, project.name,
                          ui.reset, "->", ui.white, real_dest)
            configure_args = {
                "version"   : self.version,
                "hosted"    : self.hosted,
                "debug"     : self.debug,
                "rel_paths" : True,
            }
            project.configure(**configure_args)
            project.build()
            project.install(real_dest)

    def get_dep_projects(self):
        """ Get the list of project deps

        """
        if self.single:
            return [self.base_project]
        projects = list()
        dep_tree = dict()
        for project in self.doc_worktree.doc_projects:
            dep_tree[project.name] = project.depends
        base_name = self.base_project.name
        sorted_names = qisys.sort.topological_sort(dep_tree, [base_name])
        for name in sorted_names:
            project = self.doc_worktree.get_doc_project(name, raises=False)
            if project:
                projects.append(project)
        return projects
