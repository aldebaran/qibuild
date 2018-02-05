# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import qisys.sort
from qisys.qixml import etree


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
            dep_project = self.build_worktree.get_build_project(name,
                                                                raises=False)
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
        build_project_names = [x.name for x in
                               self.build_worktree.build_projects]

        dep_packages = list()
        for name in sorted_names:
            dep_package = toolchain.get_package(name, raises=False)
            if dep_package:
                dep_packages.append(dep_package)
        res = toolchain.solve_deps(dep_packages, dep_types=dep_types)
        res = [p for p in res if p.name not in build_project_names]
        return res

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

    def get_host_projects(self, projects):
        """ Get a sorted list of all the projects listed as host dependencies """
        host_deps = set()
        dep_projects = self.get_dep_projects(projects, ["build", "runtime", "test"])
        for project in dep_projects:
            host_deps = host_deps.union(project.host_depends)

        host_projects = [self.build_worktree.get_build_project(x, raises=False)
                         for x in host_deps]
        host_projects = filter(None, host_projects)
        return host_projects

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

        # first, fill up dict with packages dependencies ...
        toolchain = self.build_worktree.toolchain
        if toolchain:
            for package in toolchain.packages:
                package.load_deps()
            package_deps = gen_deps(toolchain.packages, dep_types)
            to_sort.update(package_deps)

        # then with project dependencies
        project_deps = gen_deps(self.build_worktree.build_projects, dep_types)

        to_sort.update(project_deps)

        return qisys.sort.topological_sort(to_sort, [x.name for x in projects])


def read_deps_from_xml(target, xml_elem):
    """ Read all the ``<depends />`` tags in the xml element and set
    ``target.build_depends``, ``target.run_depends``,
    ``target.test_depends``

    """
    depends_trees = xml_elem.findall("depends")

    for depends_tree in depends_trees:
        buildtime = qisys.qixml.parse_bool_attr(depends_tree, "buildtime")
        runtime = qisys.qixml.parse_bool_attr(depends_tree, "runtime")
        testtime = qisys.qixml.parse_bool_attr(depends_tree, "testtime")
        host = qisys.qixml.parse_bool_attr(depends_tree, "host")
        dep_names = qisys.qixml.parse_list_attr(depends_tree, "names")
        for dep_name in dep_names:
            if buildtime:
                target.build_depends.add(dep_name)
            if runtime:
                target.run_depends.add(dep_name)
            if testtime:
                target.test_depends.add(dep_name)
            if host:
                target.host_depends.add(dep_name)


def dump_deps_to_xml(subject, xml_elem):
    if subject.build_depends:
        build_dep_elem = etree.SubElement(xml_elem, tag="depends")
        build_dep_elem.set("buildtime", "true")
        build_dep_elem.set("names", " ".join(subject.build_depends))
    if subject.run_depends:
        runtime_dep_elem = etree.SubElement(xml_elem, tag="depends")
        runtime_dep_elem.set("runtime", "true")
        runtime_dep_elem.set("names", " ".join(subject.run_depends))
    if subject.test_depends:
        test_dep_elem = etree.SubElement(xml_elem, tag="depends")
        test_dep_elem.set("testtime", "true")
        test_dep_elem.set("names", " ".join(subject.test_depends))


def gen_deps(objects_with_dependencies, dep_types):
    """ Generate a dictionary name -> dependencies for the objects
    passed as parameters (projects or packages)

    """
    res = dict()
    for object_with_dependencies in objects_with_dependencies:
        deps = set()
        if "build" in dep_types:
            deps.update(object_with_dependencies.build_depends)
        if "runtime" in dep_types:
            deps.update(object_with_dependencies.run_depends)
        if "test" in dep_types:
            deps.update(object_with_dependencies.test_depends)
        res[object_with_dependencies.name] = deps
    return res
