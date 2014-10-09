import qisys.sort

class DepsSolver(object):
    """ Solve dependencies across projects in a build worktree
    and packages in a toolchain

    """
    def __init__(self, build_worktree):
        self.build_worktree = build_worktree

    def get_dep_projects(self, projects, dep_types, reverse=False):
        """ Solve the dependencies of the list of projects

        :param: dep_types A list of dependencies types
                (``["build"]``, ``["runtime", "test"]``, etc.)
        :return: a list of projects in the build worktree

        """
        sorted_names = self._get_sorted_names(projects, dep_types,
                                              reverse=reverse)

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
        if not toolchain:
            return list()
        build_project_names = [x.name for x in self.build_worktree.build_projects]

        dep_packages = list()
        for name in sorted_names:
            dep_package = toolchain.get_package(name, raises=False)
            if dep_package:
                if dep_package.name not in build_project_names:
                    dep_packages.append(dep_package)
        return toolchain.solve_deps(dep_packages, dep_types=dep_types)

    def get_sdk_dirs(self, project, dep_types):
        """ Get the list of build/sdk dirs on which the project depends
        Those will then be written in build/dependencies.cmake and added
        to CMAKE_PREFIX_PATH by qibuild-config.cmake

        """
        res = list()
        dep_projects = self.get_dep_projects([project], dep_types)
        for dep_project in dep_projects:
            if dep_project.name == project.name:
                continue
            res.append(dep_project.sdk_directory)
        return res


    def _get_sorted_names(self, projects, dep_types, reverse=False):
        """ Helper for get_dep_* functions """
        if reverse:
            reverse_deps = set()
            for project in self.build_worktree.build_projects:
                if "build" in dep_types:
                    if any(x.name in project.build_depends for x in projects):
                        reverse_deps.add(project.name)
                if "runtime" in dep_types:
                    if any(x.name in project.run_depends for x in projects):
                        reverse_deps.add(project.name)
                if "test" in dep_types:
                    if any(x.name in project.test_depends for x in projects):
                        reverse_deps.add(project.name)
            return sorted(list(reverse_deps))

        to_sort = dict()
        for project in self.build_worktree.build_projects:
            deps = set()
            if "build" in dep_types:
                deps.update(project.build_depends)
            if "runtime" in dep_types:
                deps.update(project.run_depends)
            if "test" in dep_types:
                deps.update(project.test_depends)
            to_sort[project.name] = deps
        return qisys.sort.topological_sort(to_sort, [x.name for x in projects])


def read_deps_from_xml(object, xml_elem):
    """ Read all the ``<depends />`` tags in the xml element and set
    ``object.build_depends``, ``object.run_depends``,
    ``object.test_depends``

    """
    depends_trees = xml_elem.findall("depends")

    for depends_tree in depends_trees:
        buildtime = qisys.qixml.parse_bool_attr(depends_tree, "buildtime")
        runtime   = qisys.qixml.parse_bool_attr(depends_tree, "runtime")
        testtime  = qisys.qixml.parse_bool_attr(depends_tree, "testtime")
        dep_names = qisys.qixml.parse_list_attr(depends_tree, "names")
        for dep_name in dep_names:
            if buildtime:
                object.build_depends.add(dep_name)
            if runtime:
                object.run_depends.add(dep_name)
            if testtime:
                object.test_depends.add(dep_name)
