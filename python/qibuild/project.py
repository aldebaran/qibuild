import os
import platform

from qisys import ui
import qisys.command
import qisys.sh
import qibuild.cmake
import qibuild.build

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
        """ Path to qiproject.xml """
        return os.path.join(self.path, "qiproject.xml")

    @property
    def build_directory(self):
        """ Return a suitable build directory, depending on the
        build setting of the worktree: the name of the toolchain,
        the build profiles, and the build type (debug/release)

        """
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
        """ The list of CMake arguments to use when configuring the
        project.
        Delegates to build_config.cmake_args

        """
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
        cmd += qibuild.build.num_jobs_to_args(num_jobs, cmake_generator)

        make_env = os.environ.copy()
        if verbose_make:
            if "Makefiles" in self.cmake_generator:
                make_env["VERBOSE"] = "1"
            if self.cmake_generator == "Ninja":
                cmd.append("-v")
        try:
            qisys.command.call(cmd, env=make_env)
        except qisys.command.CommandFailedException:
            raise qibuild.build.BuildFailed(self)

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
