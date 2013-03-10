import os
import platform

import qisys.worktree
from qibuild.dependencies_solver import topological_sort
import qibuild.build_config

class BuildWorkTreeError(Exception):
    pass

class BuildWorkTree(qisys.worktree.WorkTreeObserver):
    """

    """
    def __init__(self, worktree):
        self.worktree = worktree
        self.root = self.worktree.root
        self.build_config = qibuild.build_config.CMakeBuildConfig()
        self.build_projects = self._load_build_projects()
        worktree.register(self)

    @property
    def qibuild_xml(self):
        config_path = os.path.join(self.worktree.dot_qi, "qibuild.xml")
        if not os.path.exists(config_path):
            with open(config_path, "w") as fp:
                fp.write("<qibuild />\n")
        return config_path

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
            build_project.cmake_args = self.build_config.cmake_args[:]
        return build_projects



class BuildProject(object):
    def __init__(self, build_worktree, worktree_project):
        self.build_worktree = build_worktree
        self.build_config = build_worktree.build_config
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

    @property
    def build_directory(self):
        parts = list()
        toolchain = self.build_config.toolchain
        build_type = self.build_config.build_type
        visual_studio = self.build_config.visual_studio
        if toolchain:
            parts.append(toolchain.name)
        else:
            parts.append("sys-%s-%s" % (platform.system().lower(),
                                        platform.machine().lower()))
        profiles = self.build_config.profiles
        for profile in profiles:
            parts.append(profile.name)

        # When using cmake + visual studio, sharing the same build dir with
        # several build config is mandatory.
        # Otherwise, it's not a good idea, so we always specify it
        # when it's not "Debug" (the default)
        if not visual_studio:
            if build_type and build_type != "Debug":
                parts.append(build_type.lower())



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
