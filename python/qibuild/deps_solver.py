import qisys.sort

class DepsSolver(object):
    def __init__(self, build_worktree):
        self.build_worktree = build_worktree

    def get_dep_projects(self, projects, dep_types):
        """ Solve the dependencies of the list of projects

        :param: dep_types A list of dependencies types
                (``["build"]``, ``["runtime", "test"]``, etc.)
        :return: a list of projects in the build worktree

        """
        sorted_names = self._get_sorted_names(projects, dep_types)

        dep_projects = list()
        for name in sorted_names:
            dep_project = self.build_worktree.get_build_project(name, raises=False)
            if dep_project:
                dep_projects.append(dep_project)
        return dep_projects

    def get_dep_packages(self, projects, dep_types):
        """ Solve the dependencies of the list of projects

        :param: dep_types A list of dependencies types
                (``["build"]``, ``["runtime", "test"]``, etc.)
        :return: a list of packages in the build worktree's toolchain

        """
        sorted_names = self._get_sorted_names(projects, dep_types)
        toolchain = self.build_worktree.toolchain

        dep_packages = list()
        for name in sorted_names:
            dep_package = toolchain.get_package(name, raises=False)
            if dep_package:
                dep_packages.append(dep_package)
        return dep_packages


    def _get_sorted_names(self, projects, dep_types):
        """ Helper for get_dep_* functions """
        to_sort = dict()
        for project in projects:
            deps = set()
            if "build" in dep_types:
                deps = deps.union(project.depends)
            if "runtime" in dep_types:
                deps = deps.union(project.depends)
            to_sort[project.name] = deps
        return qisys.sort.topological_sort(to_sort, [x.name for x in projects])
