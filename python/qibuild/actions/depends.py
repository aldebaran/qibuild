# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

""" Display dependencies of projects

"""

import qisys.ui
import qibuild.deps
import qibuild.parsers


def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.cmake_build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("depends arguments",
                                      description="Shows project and package dependencies."
                                      "\nUse --runtime, --direct, and --reverse to control "
                                      "the dependencies to examine. Default usage shows "
                                      "compressed, recursive, build time dependencies. "
                                      "\nUse --tree or --graph to control the output format."
                                      "\nFor best results with --graph, use:\nqibuild depends "
                                      "--graph | dot -Tpng -oout.png -Goverlap=scale -Gsplines=true")
    group.add_argument("--runtime", action="store_true", default=False,
                       help="use runtime dependencies only")
    group.add_argument("--reverse", action="store_true", default=False,
                       help="show projects that depend on the current project")
    group.add_argument("--tree", action="store_true", default=False,
                       help="output in text tree format showing paths")
    group.add_argument("--graph", action="store_true",
                       help="output in format suitable for the \"dot\" "
                       "graphing tool")
    group.add_argument("--direct", action="store_true", default=False,
                       help="only display direct dependencies")


class DependencyRelationship(object):
    """ helper class to separate dependency search from display """

    def __init__(self, from_name, to_name):
        self.from_name = from_name
        self.to_name = to_name
        self.path = ""
        self.is_package = False
        self.is_known = False
        self.depth = 0

    def __str__(self):
        return "Dependency from %s to %s, is_package: %s, is_known: %s, depth: %s" % (
            self.from_name, self.to_name, self.is_package, self.is_known, self.depth)

    def same_as(self, other):
        """ return true if from_name and to_name are the same """
        return (other.from_name == self.from_name and
                other.to_name == self.to_name)


def get_deps(build_worktree, project, single, runtime, reverse):
    """ create a list of DependencyRelationship objects ready for display """
    deps_solver = qibuild.deps.DepsSolver(build_worktree)
    if reverse:
        (packages, projects) = (set(), build_worktree.build_projects)
    else:
        if runtime:
            dep_types = ["build"]
        else:
            dep_types = ["runtime"]
        projects = deps_solver.get_dep_projects([project], dep_types)
        packages = deps_solver.get_dep_packages([project], dep_types)

    # Remove self from projects
    projects = [x for x in projects if x.name is not project.name]

    if reverse:
        collected_dependencies = collect_dependencies_reverse(
            project, projects, single, runtime)
    else:
        collected_dependencies = collect_dependencies(
            project, projects, packages, single, runtime)

    return collected_dependencies


def print_deps_tree(dependency_relationships):
    """ --tree style output formatter """
    if not dependency_relationships:
        qisys.ui.info("None")
        return
    max_name = max(
        [len(x.to_name + "    "*x.depth) for x in dependency_relationships])
    for dep in dependency_relationships:
        color = qisys.ui.blue
        if dep.is_package:
            color = qisys.ui.white
        if not dep.is_known:
            color = qisys.ui.red
        item = "  " + "    "*dep.depth + dep.to_name
        qisys.ui.info(color, item.ljust(max_name+2), qisys.ui.reset, dep.path)


def separate_into_groups(dependency_relationships):
    """ split into sorted logical groups """
    projects = list()
    projects_bad = list()
    packages = list()
    packages_bad = list()

    for dep in dependency_relationships:
        if dep.is_package:
            if dep.is_known:
                packages.append(dep.path)
            elif not dep.is_known:
                packages_bad.append(dep.to_name)
        else:
            if dep.is_known:
                projects.append(dep.path)
            elif not dep.is_known:
                projects_bad.append(dep.to_name)

    projects = sorted(set(projects))
    projects_bad = sorted(set(projects_bad))
    packages = sorted(set(packages))
    packages_bad = sorted(set(packages_bad))
    return projects, projects_bad, packages, packages_bad


def print_deps_compressed(dependency_relationships):
    """ default simple compressed output formatter """
    if not dependency_relationships:
        qisys.ui.info("None")
        return

    (projects, projects_bad, packages, packages_bad) = separate_into_groups(
        dependency_relationships)

    if len(projects) + len(projects_bad) > 0:
        qisys.ui.info(qisys.ui.reset, "  Projects")
        for project in projects:
            qisys.ui.info(qisys.ui.white, "    " + project)
        for project in projects_bad:
            qisys.ui.info(qisys.ui.red, "    " + project)
    if len(packages) + len(packages_bad) > 0:
        qisys.ui.info(qisys.ui.reset, "  Packages")
        for package in packages:
            qisys.ui.info(qisys.ui.white, "    " + package)
        for package in packages_bad:
            qisys.ui.info(qisys.ui.red, "    " + package)


def print_deps_graph(root_name, label, dependency_relationships):
    """ --graph output, suitable for dot """
    # header
    qisys.ui.info(qisys.ui.reset, "digraph", qisys.ui.green,
                  "\"" + root_name + "\"", qisys.ui.reset, "{")
    qisys.ui.info(qisys.ui.reset, "  label=",
                  qisys.ui.green, "\"" + label + "\"")

    cleaned = list()
    # TODO cleaner duplicate removal (depth could be different)
    for dep in dependency_relationships:
        if not next((y for y in cleaned if y.same_as(dep)), None):
            cleaned.append(dep)
    dependency_relationships = cleaned

    # Show unique packages as rectangles
    package_names = sorted(set(
        x.to_name for x in dependency_relationships if x.is_package))
    for package_name in package_names:
        qisys.ui.info(qisys.ui.reset, "  \"" + package_name + "\" [shape=box]")

    for dep in dependency_relationships:
        src_color = qisys.ui.blue
        if dep.from_name == root_name:
            src_color = qisys.ui.green

        dest_color = qisys.ui.blue
        line_type = ""
        if dep.is_package:
            dest_color = qisys.ui.white
        if not dep.is_known:
            dest_color = qisys.ui.red
            line_type = "[style=dotted]"
        qisys.ui.info(src_color, "  " + "  "*dep.depth,
                      "\"" + dep.from_name + "\"",
                      qisys.ui.reset, "->",
                      dest_color, "\"" + dep.to_name + "\"",
                      qisys.ui.reset, line_type)
    qisys.ui.info(qisys.ui.reset, "}")


def collect_dependencies_reverse(project, projects, single, runtime, depth=0):
    """ recursively collects projects that depends on the current project """
    collected_dependencies = list()
    for proj in projects:
        dependency = None
        depends = list()
        if runtime:
            depends = proj.run_depends
        else:
            depends = proj.build_depends
        if project.name in depends:
            dependency = DependencyRelationship(project.name, proj.name)
            dependency.is_known = True
            dependency.path = proj.path
            dependency.depth = depth
            collected_dependencies.append(dependency)
            if not single:
                sub = collect_dependencies_reverse(
                    proj, projects, False, runtime, depth+1)
                collected_dependencies.extend(sub)

    return collected_dependencies


def package_names_first(dependency_names, package_names):
    """ put package names first """
    dep_packages = sorted(
        [x for x in dependency_names if x in package_names])
    dep_projects = sorted(
        [x for x in dependency_names if x not in package_names])
    dep_packages.extend(dep_projects)
    return dep_packages


def collect_dependencies(project, projects, packages, single, runtime, depth=0):
    """ recursively collect dependent projects and packages """
    if depth > 99:
        qisys.ui.error("Probable recursion problem: ", project.name)
        exit(1)

    # Look at runtime dependencies if runtime
    if runtime:
        dependency_names = project.run_depends
    else:
        dependency_names = project.build_depends
    package_names = [package.name for package in packages]
    dependency_names = package_names_first(dependency_names, package_names)
    collected_dependencies = list()

    # Go through them and gather information
    for dependency_name in dependency_names:
        dependency = DependencyRelationship(project.name, dependency_name)
        dependency.depth = depth
        next_item = None

        if dependency_name in package_names:
            dependency.is_package = True
            # find package, so that we can get its path
            match = next(
                (x for x in packages if x.name == dependency_name), None)
            if match:
                dependency.path = match.path
                dependency.is_known = True
        else:
            # find project, so that we can get its directory
            match = next(
                (x for x in projects if x.name == dependency_name), None)
            if match:
                dependency.path = match.path
                dependency.is_known = True
                next_item = match
        collected_dependencies.append(dependency)

        if not single and next_item:
            collected_dependencies.extend(
                collect_dependencies(next_item, projects, packages,
                                     False, runtime, depth+1))
    return collected_dependencies


def do(args):
    """Main entry point for depends action"""
    build_worktree = qibuild.parsers.get_build_worktree(args, verbose=(not args.graph))
    project = qibuild.parsers.get_one_build_project(build_worktree, args)
    collected_dependencies = get_deps(
        build_worktree, project, args.direct, args.runtime, args.reverse)

    # create title
    label = project.name
    if args.runtime:
        label = label + " run time"
    else:
        label = label + " build time"
    if args.direct:
        label = label + " direct"
    if args.reverse:
        label = label + " reverse dependencies"
    else:
        label = label + " dependencies"

    # display
    if args.graph:
        print_deps_graph(project.name, label, collected_dependencies)
    else:
        qisys.ui.info(qisys.ui.green, label)
        if args.tree:
            print_deps_tree(collected_dependencies)
        else:
            print_deps_compressed(collected_dependencies)
