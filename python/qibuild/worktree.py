import os
import platform

from qisys import ui
import qisys.command
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
        return build_projects

    def configure_build_profile(self, name, flags):
        """ Configure a build profile for the worktree """
        qibuild.profile.configure_build_profile(self.qibuild_xml,
                                                name, flags)


    def remove_build_profile(self, name):
        """ Remove a build profile for this worktree """
        qibuild.profile.configure_build_profile(self.qibuild_xml, name)



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
        parts = ["build"]
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

        # FIXME: handle custom build dir
        return os.path.join(self.path, "-".join(parts))

    @property
    def cmake_args(self):
        return self.build_config.cmake_args(self.build_worktree)

    def configure(self, **kwargs):
        """ Delegate to qibuild.cmake """
        # FIXME: done by write_dependencies
        qisys.sh.mkdir(self.build_directory, recursive=True)
        cmake_args = self.cmake_args
        qibuild.cmake.cmake(self.path, self.build_directory,
                            cmake_args, **kwargs)

    def build(self, num_jobs=1, rebuild=False, target=None, fix_shared_libs=True,
              verbose_make=False, coverity=False):
        """ Build the project """
        timer = ui.timer("make %s" % self.name)
        timer.start()
        build_type = self.build_config.build_type
        cmake_generator = self.build_config.cmake_generator

        cmd = []
        if coverity:
            if not qisys.command.find_program("cov-build"):
                raise Exception("cov-build was not found on the system")
            cov_dir = os.path.join(self.build_directory, "coverity")
            qisys.sh.mkdir(cov_dir)
            cmd += ["cov-build", "--dir", cov_dir]

        cmd += ["cmake", "--build", self.build_directory,
                         "--config", build_type]

        if target:
            cmd += ["--target", target]

        if rebuild:
            cmd += ["--clean-first"]
        cmd += [ "--" ]
        cmd += num_jobs_to_args(num_jobs, cmake_generator)

        make_env = os.environ.copy()
        if verbose_make:
            if "Makefiles" in self.cmake_generator:
                make_env["VERBOSE"] = "1"
            if self.cmake_generator == "Ninja":
                cmd.append("-v")
        try:
            qisys.command.call(cmd, env=make_env)
        except qisys.command.CommandFailedException:
            raise BuildFailed(self)

        if fix_shared_libs:
            self.fix_shared_libs()
        timer.stop()

    def fix_shared_libs(self):
        # FIXME !
        pass


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

def num_jobs_to_args(num_jobs, cmake_generator):
    """ Convert a number of jobs to a list of cmake args

    >>> num_jobs_to_args(3, "Unix Makefiles")
    ["-j", "3"]

    >>> num_jobs_to_args(3, "NMake Makefiles"
    Error: -j is not supported for NMake, use Jom

    >>> num_jobs_to_args(3, "Visual Studio")
    Warning: -j is ignored for Visual Studio

    """

    if num_jobs == 1:
        return list()
    if "Unix Makefiles" in cmake_generator or \
       "Ninja" in cmake_generator:
        return ["-j", str(num_jobs)]
    if cmake_generator == "NMake Makefiles":
        mess   = "-j is not supported for %s\n" % cmake_generator
        mess += "On windows, you can use Jom instead to compile "
        mess += "with multiple processors"
        raise Exception(mess)
    if "Visual Studio" in cmake_generator or \
        cmake_generator == "Xcode" or \
        "JOM" in cmake_generator:
        ui.warning("-j is ignored when used with", cmake_generator)
        return list()
    ui.warning("cannot parse -j into a cmake option for generator: %s" % cmake_generator)
    return list()

class BuildFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when building project %s" % self.project.name
