import os

import qisys.worktree
from qibuild.dependencies_solver import topological_sort

class BuildWorkTreeError(Exception):
    pass

class BuildWorkTree(qisys.worktree.WorkTreeObserver):
    """

    """
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = self.worktree.root
        self.build_projects = self._load_build_projects()
        worktree.register(self)

    def get_build_project(self, name, raises=True):
        """ Get a build project given its name """
        for build_project in self.build_projects:
            if build_project.name == name:
                return build_project
        if raises:
            raise BuildWorkTreeError("No such qibuild project: %s" % name)

    def get_deps(self, top_project, runtime=False, build_deps_only=False):
        """ Get the depencies of a project """
        to_sort = dict()
        if build_deps_only:
            for project in self.build_projects:
                to_sort[project.name] = project.depends
        elif runtime:
            for project in self.build_projects:
                to_sort[project.name] = project.rdepends
        else:
            for project in self.build_projects:
                to_sort[project.name] = project.rdepends.union(project.depends)

        names = topological_sort(to_sort, [top_project.name])
        deps = list()
        for name in names:
            dep_project = self.get_build_project(name, raises=False)
            if dep_project:
                deps.append(dep_project)
        return deps

    def on_project_added(self, project):
        """ Called when a new project has been registered """
        self.build_projects = self._load_build_projects()

    def on_project_removed(self, project):
        """ Called when a build project has been removed """
        self.build_projects = self._load_build_projects()

    def _load_build_projects(self):
        """ Create BuildProject for every buildable project in the
        worktree

        """
        build_projects = list()
        for wt_project in self.worktree.projects:
            if not os.path.exists(wt_project.qiproject_xml):
                continue
            build_project = BuildProject(self, wt_project)
            build_projects.append(build_project)
        return build_projects


class BuildProject(object):
    def __init__(self, build_worktree, worktree_project):
        self.build_worktree = build_worktree
        self.path = worktree_project.path
        self.src = worktree_project.src
        self.name = None
        # depends is a set at this point because they are not sorted yet
        self.depends = set()
        self.rdepends = set()
        self.parse_qiproject_xml()

    @property
    def qiproject_xml(self):
        return os.path.join(self.path, "qiproject.xml")

    def parse_qiproject_xml(self):
        parser = BuildProjectParser(self)
        xml_elem = qisys.qixml.read(self.qiproject_xml).getroot()
        parser.parse(xml_elem)

    def __repr__(self):
        return "<BuildWorkTree %s in %s>" % (self.name, self.src)



class BuildProjectParser:
    def __init__(self, target):
        self.target = target

    def parse(self, xml_elem):
        # FIXME: support new syntax
        self.target.name = qisys.qixml.parse_required_attr(xml_elem, "name")
        # Read depends:
        depends_trees = xml_elem.findall("depends")
        for depends_tree in depends_trees:
            buildtime = qisys.qixml.parse_bool_attr(depends_tree, "buildtime")
            runtime   = qisys.qixml.parse_bool_attr(depends_tree, "runtime")
            dep_names = qisys.qixml.parse_list_attr(depends_tree, "names")
            if buildtime:
                for dep_name in dep_names:
                    self.target.depends.add(dep_name)
            if runtime:
                for dep_name in dep_names:
                    self.target.rdepends.add(dep_name)
