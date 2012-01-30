## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This module contains the Toc class.
which is where all the 'magic' happens ....

"""

import os
import glob
import platform
import logging
import operator

import qibuild
import qitoolchain

from qibuild.project  import Project
from qibuild.worktree import WorkTree
from qibuild.command  import CommandFailedException
from qibuild.dependencies_solver import DependenciesSolver

LOGGER = logging.getLogger("qibuild.toc")


class TocException(Exception):
    """Custom exception.
    Specific exceptions raised by toc are of this type,
    so they can be caught by callers.
    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message

class ConfigureFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when configuring project %s" % self.project.name

class BuildFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when building project %s" % self.project.name

class TestsFailed(Exception):
    def __init__(self, project, summary):
        self.project = project
        self.summary = summary
    def __str__(self):
        res  = "Error occured when testing project %s\n" % self.project.name
        res += self.summary
        return res

class InstallFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when installing project %s" % self.project.name


class Toc(WorkTree):
    """This class contains a list of packages, and a list of projects.

    It is also capable of sorting dependencies.

    It also store various configurations, to be sure it is consistent
    across the projects.

    This class also contains "high-level" functions.

    Example of use:

        toc = Toc("/path/to/work/tree", "release", ...)
        # Look for the foo project in the worktree
        foo = toc.get_project("foo")
        # Resolve foo dependencies, call cmake on each of them,
        toc.configure_project(foo)
        # Build the foo project, building all the dependencies in
        # the correct order:
        toc.build_project(foo)

    """
    def __init__(self, work_tree,
            path_hints=None,
            config=None,
            build_type="debug",
            cmake_flags=None,
            cmake_generator=None,
            active_projects=None,
            solve_deps=True):
        """
            work_tree       : see WorkTree.__init__
            path_hints      : see WorkTree.__init__

            build_type      : a build type, could be debug or release (defaults to debug)
            cmake_flags     : optional additional cmake flags
            cmake_generator : optional cmake generator (defaults to Unix Makefiles)
            active_projects : the projects excplicitely specified by user
        """
        WorkTree.__init__(self, work_tree, path_hints=path_hints)
        # The local config file in which to write
        self.config_path = os.path.join(self.work_tree, ".qi", "qibuild.xml")

        # When you are running toc actions for a qibuild project, sometimes
        # a Toc object is created on the fly (Using toc_open with a non
        # empty path_hints) variable.
        # In this case, the .qi directory may not even exists, nor the
        # .qi directory, so create it:
        if not os.path.exists(self.config_path):
            to_create = os.path.dirname(self.config_path)
            qibuild.sh.mkdir(to_create, recursive=True)
            with open(self.config_path, "w") as fp:
                fp.write("<qibuild />\n")
        # Perform format conversion if necessary
        handle_old_qibuild_cfg(self.work_tree)
        handle_old_qibuild_xml(self.work_tree)

        # Handle config:
        self.config = qibuild.config.QiBuildConfig(config)
        self.config.read()
        self.config.read_local_config(self.config_path)
        self.active_config = self.config.active_config

        self.build_type = build_type
        if not self.build_type:
            self.build_type = "debug"

        # The cmake flags set by the user will always be added
        # to the actual cmake flags used by the Toc oject,
        # but we may add other flags when using a toolchain.
        # see self.update_cmake_flags()
        self.cmake_flags       = list()
        self.cmake_generator   = cmake_generator
        self.build_folder_name = None

        # Set build environment
        envsetter = qibuild.envsetter.EnvSetter()
        envsetter.read_config(self.config)
        self.build_env =  envsetter.get_build_env()

        # List of objects of type qibuild.project.Project,
        # this is updated using WorkTree.buildable_projects
        self.projects          = list()

        # The list of projects the user asked for from command
        # line.
        # Set by toc_open()
        if not active_projects:
            self.active_projects = list()
        else:
            self.active_projects = active_projects
        self.solve_deps = solve_deps

        # Set cmake generator if user has not set if in Toc ctor:
        if not self.cmake_generator:
            self.cmake_generator = self.config.cmake.generator
            if not self.cmake_generator:
                self.cmake_generator = "Unix Makefiles"

        # Read the current config, create toolchain and pacakges object
        # if necessary
        self.packages = list()
        self.toolchain = None
        if self.active_config is not None:
            if self.active_config in qitoolchain.get_tc_names():
                self.toolchain = qitoolchain.Toolchain(self.active_config)
                self.packages  = self.toolchain.packages
            else:
                # The config does not match a toolchain
                local_dir = os.path.join(self.work_tree, ".qi")
                local_cmake = os.path.join(local_dir, "%s.cmake" % self.active_config)
                if not os.path.exists(local_cmake):
                    mess  = """Invalid configuration {active_config}
 * No toolchain named {active_config}. Known toolchains are:
    {tc_names}
 * No custom cmake file for config {active_config} found.
   (looked in {local_cmake})
"""
                    raise TocException(mess.format(active_config=self.active_config,
                        local_cmake = local_cmake,
                        tc_names = qitoolchain.get_tc_names()))

        # Useful vars to cope with Visual Studio quirks
        self.using_visual_studio = "Visual Studio" in self.cmake_generator
        self.vc_version = self.cmake_generator.split()[-1]

        # The actual list of cmake flags we are going to use
        # will be computed during self.configure_project.
        # Right now, we will just store the flags passed in ctor
        # in self.user_cmake_flags, to be sure they are always added
        # at the end of the list of flags
        if cmake_flags:
            self.user_cmake_flags = cmake_flags[:]
        else:
            self.user_cmake_flags = list()

        # Finally, update the build configuration of all the projects
        # (this way we are sure that the build configuration is the same for
        # every project)
        self.update_projects()


    def save_config(self):
        """ Save configuration. You should call this after changing
        self.config in order to make the changes permanent

        """
        self.config.write_local_config(self.config_path)
        self.config.write()

    def update_projects(self):
        """Set self.projects() with the correct build configs and correct build folder
        name.

        This make sure that every project managed by a Toc instance has the correct
        build config, and the same build folder

        """
        self.set_build_folder_name()

        # self.buildable_projects has been set by WorkTree.__init__
        for pname, ppath in self.buildable_projects.iteritems():
            project = Project(pname, ppath)
            self.projects.append(project)

        # Small warning here: when we update the projects, we do NOT
        # have the complete list of the projects, their dependencies,
        # the list of sdk dirs, and so on ...
        # So we only call qibuild.projects.bootstrap_project() at the last
        # moment...
        for project in self.projects:
            qibuild.project.update_project(project, self)

        self.projects.sort(key=operator.attrgetter('name'))


    def set_build_folder_name(self):
        """Get a reasonable build folder.
        The point is to be sure we don't have two incompatible build configurations
        using the same build dir.

        Return a string looking like
        build-linux-release
        build-cross-debug ...
        """
        res = list()

        if self.active_config:
            res.append(self.active_config)
        else:
            res.append("sys-%s-%s" % (platform.system().lower(), platform.machine().lower()))

        if not self.using_visual_studio and self.build_type != "debug":
            # When using cmake + visual studio, sharing the same build dir with
            # several build config is mandatory.
            # Otherwise, it's not a good idea, so we always specify it
            # when it's not "debug" (the default)
            res.append(self.build_type)

        self.build_folder_name = "-".join(res)

    def get_project(self, project_name):
        """Return a project from a name.

        Raise a TocException if the project was not found
        """
        res = [p for p in self.projects if p.name == project_name]
        if len(res) == 1:
            return res[0]
        else:
            raise TocException("No such project: %s" % project_name)


    def get_sdk_dirs(self, project_name):
        """ Return a list of sdk needed to build a project.

        Iterate through the dependencies.
        When it is a package (pre-compiled), add the path of
        the package, when it is a project, add the path to the "sdk" dir
        under the build directory of the project.

        If a name is both in source and in package, use the package
        (saves compile time), unless user asked explicitely for a list
        of projects
        """
        dirs = list()

        known_project_names = [p.name for p in self.projects]
        if project_name not in known_project_names:
            raise TocException("%s is not a buildable project" % project_name)

        # Here do not honor self.solve_deps or the software won't compile :)
        dep_solver = DependenciesSolver(projects=self.projects, packages=self.packages,
            active_projects=self.active_projects)
        (r_project_names, _package_names, not_found) = dep_solver.solve([project_name])

        # Nothing to do with with the packages:
        # SDK dirs from toolchain are managed by the toolchain file in
        # self.toolchain

        if not_found:
            # FIXME: right now there are tons of case where you could have missing
            # projects. (using a cross-toolchain, or an Aldebaran SDK)
            # Put this back later.
            # LOGGER.warning("Could not find projects %s", ", ".join(not_found))
            pass

        # Remove self from the list:
        r_project_names.remove(project_name)


        for project_name in r_project_names:
            project = self.get_project(project_name)
            dirs.append(project.get_sdk_dir())

        LOGGER.debug("sdk_dirs for %s : %s", project_name, dirs)
        return dirs


    def resolve_deps(self, runtime=False):
        """ Return a tuple of three lists:
        (projects, package, not_foud), see qibuild.dependencies_solver
        for more documentation.

        """
        if not self.solve_deps:
            return (self.active_projects, list(), list())
        else:
            dep_solver = DependenciesSolver(projects=self.projects,
                                            packages=self.packages,
                                            active_projects=self.active_projects)
            return dep_solver.solve(self.active_projects,
                                    runtime=runtime)

    def configure_project(self, project, clean_first=True):
        """ Call cmake with correct options

        Note: the cmake flags (CMAKE_BUILD_TYPE, or the -D args coming
        from qibuild configure -DFOO_BAR) have already been passed via
        the toc object. See qibuild.toc.toc_open() and the ctor of
        Project for the details.

        Note2: if toolchain file is not None, the flag CMAKE_TOOLCHAIN_FILE
            will be set.

        Note3: if clean_first is False, we won't delete CMake's cache.
        This is mainly useful when you are calling cmake NOT from
        `qibuild configure'.
        """
        if not os.path.exists(project.directory):
            raise TocException("source dir: %s does not exist, aborting" % project.directory)
        cmake_file = os.path.join(project.directory, "CMakeLists.txt")
        if not os.path.exists(cmake_file):
            mess = """{project.name} does not look like a valid CMake project!
        (No CMakeLists.txt in {project.directory})
        """.format(project=project)
            raise TocException(mess)

        # Generate the dependencies.cmake just in time:
        qibuild.project.bootstrap_project(project, self)

        # Set generator if necessary
        cmake_args = list()
        if self.cmake_generator:
            cmake_args.extend(["-G", self.cmake_generator])

        cmake_flags = list()
        cmake_flags.extend(project.cmake_flags)

        if self.toolchain is not None:
            tc_file = self.toolchain.toolchain_file
            toolchain_path = qibuild.sh.to_posix_path(tc_file)
            cmake_flags.append('CMAKE_TOOLCHAIN_FILE=%s' % toolchain_path)

        # Finally append user's cmake flags (passed in ctor)
        cmake_flags.extend(self.user_cmake_flags)

        cmake_args.extend(["-D" + x for x in cmake_flags])

        if "MinGW" in self.cmake_generator:
            paths = self.build_env["PATH"].split(os.pathsep)
            paths_withoutsh = list()
            for p in paths:
                if not os.path.exists(os.path.join(p, "sh.exe")):
                    paths_withoutsh.append(p)
            self.build_env["PATH"] = os.pathsep.join(paths_withoutsh)

        try:
            qibuild.cmake(project.directory,
                          project.build_directory,
                          cmake_args,
                          clean_first=clean_first,
                          env=self.build_env)
        except CommandFailedException:
            raise ConfigureFailed(project)


    def build_project(self, project, incredibuild=False, num_jobs=1, target=None, rebuild=False):
        """Build a project, choosing between  Nmake, Visual Studio or make

        """
        build_dir = project.build_directory
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cmake_cache):
            _advise_using_configure(self, project)

        cmd = ["cmake", "--build", build_dir, "--config", self.build_type]
        if target:
            cmd += ["--target", target]

        if rebuild:
            cmd += ["--clean-first"]
        cmd += [ "--" ]
        # In order to use incredibuild, we have to do this small hack:
        if self.using_visual_studio:
            sln_files = glob.glob(build_dir + "/*.sln")
            assert len(sln_files) == 1, "Expecting only one sln, got %s" % sln_files
            if incredibuild:
                sln_file = sln_files[0]
                cmd = ["BuildConsole.exe", sln_file]
                cmd += ["/cfg=%s|Win32" % self.build_type]
                cmd += ["/nologo"]
                if target:
                    cmd += ["/target=%s" % target]
            else:
                if num_jobs > 1 and "visual studio" in self.cmake_generator.lower():
                    cmd += ["/m:%d" % num_jobs]

        if num_jobs > 1 and "make" in self.cmake_generator.lower():
            cmd += [ "-j%d" % num_jobs]

        try:
            qibuild.command.call(cmd, env=self.build_env)
        except CommandFailedException:
            raise BuildFailed(project)

    def test_project(self, project, test_name=None):
        """Run qibuild.ctest on a project

        :param test_name: if given, only this test will run

        """
        build_dir = project.build_directory
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cmake_cache):
            _advise_using_configure(self, project)
        (res, summary) = qibuild.ctest.run_tests(project, self.build_env,
            test_name=test_name)
        if res:
            LOGGER.info(summary)
        else:
            raise TestsFailed(project, summary)


    def install_project(self, project, destdir, runtime=False):
        """Install the project """
        build_dir = project.build_directory
        self.build_env["DESTDIR"] = destdir
        try:
            if runtime:
                self.install_project_runtime(project, destdir)
            else:
                cmd = ["cmake", "--build", build_dir, "--config", self.build_type,
                        "--target", "install"]
                qibuild.command.call(cmd, env=self.build_env)
        except CommandFailedException:
            raise InstallFailed(project)

    def install_project_runtime(self, project, destdir):
        """Install runtime component of a project to a destdir """
        runtime_components = [
             "binary",
             "data",
             "conf",
             "lib",
             "python",
             "doc"
         ]
        for component in runtime_components:
            self.build_env["DESTDIR"] = destdir
            cmake_args = list()
            cmake_args += ["-DCOMPONENT=%s" % component]
            cmake_args += ["-P", "cmake_install.cmake"]
            LOGGER.debug("Installing %s", component)
            qibuild.command.call(["cmake"] + cmake_args,
                cwd=project.build_directory,
                env=self.build_env,
                )



def _projects_from_args(toc, args):
    """
    Cases handled:
      - nothing specified: get the project from the cwd
      - args.single: do not resolve dependencies
      - args.all: return all projects
    Returns a tuple (project_names, single):
        project_names: the actual list for project
        single: user specified --single
    """
    toc_p_names = [p.name for p in toc.projects]
    if hasattr(args, "all") and args.all:
        # Pretend the user has asked for all the known projects
        LOGGER.debug("select: All projects have been selected")
        return (toc_p_names, False)

    if hasattr(args, "projects"):
        if args.projects:
            LOGGER.debug("select: projects list from arguments: %s", ",".join(args.projects))
            return ([args.projects, args.single])
        else:
            from_cwd = None
            try:
                from_cwd = project_from_cwd()
            except:
                pass
            if from_cwd:
                LOGGER.debug("select: projects from cwd: %s", from_cwd)
                return ([from_cwd], args.single)
            else:
                LOGGER.debug("select: default to all projects")
                return (toc_p_names, args.single)
    else:
        return (list(), False)


def toc_open(work_tree, args=None):
    """ Open a toc work_tree.

    """
    # Not that args can come from:
    #    - a work_tree parser
    #    - a toc parser
    #    - a build parser
    # (hence all the hasattr...)
    # ...
    # or simply not given :)
    path_hints     = list()

    config = None
    if hasattr(args, 'config'):
        config   = args.config

    build_type = None
    if hasattr(args, 'build_type'):
        build_type = args.build_type

    cmake_flags = list()
    if hasattr(args,'cmake_flags'):
        cmake_flags = args.cmake_flags

    cmake_generator = None
    if hasattr(args, 'cmake_generator'):
        cmake_generator = args.cmake_generator

    if not work_tree:
        work_tree = qibuild.worktree.guess_work_tree()
    current_project = qibuild.worktree.search_current_project_root(os.getcwd())
    if not work_tree:
        # Sometimes we you just want to create a fake worktree object because
        # you just want to build one project (no dependencies at all, no configuration...)
        # In this case, just searching for a manifest from the current working directory
        # is enough
        work_tree = current_project
        LOGGER.debug("no work tree found using the project root: %s", work_tree)

    if current_project:
        #we add the current project as a hint, see the function doc
        path_hints.append(current_project)

    if work_tree is None:
        raise TocException("Could not find a work tree, "
            "please try from a valid work tree, specify an "
            "existing work tree with '--work-tree {path}', or "
            "create a new work tree with 'qibuild init'")

    toc = Toc(work_tree,
               config=config,
               build_type=build_type,
               cmake_flags=cmake_flags,
               cmake_generator=cmake_generator,
               path_hints=path_hints)

    (active_projects, single) =  _projects_from_args(toc, args)
    toc.active_projects = active_projects
    LOGGER.debug("active projects: %s", ".".join(toc.active_projects))
    LOGGER.debug("single: %s", str(single))
    toc.solve_deps = (not single)
    return toc


def create(directory):
    """ Create a new toc work_tree inside a work tree

    """
    qibuild.worktree.create(directory)



def project_from_cwd():
    """Return a project name from the current working directory

    """
    project_dir = qibuild.worktree.search_current_project_root(os.getcwd())
    if not project_dir:
        raise Exception("Could not guess project name from the working directory.\n"
                "Please go to a subdirectory of a project\n"
                "or specify the name of the project.")
    return qibuild.project.name_from_directory(project_dir)


def _advise_using_configure(self, project):
    """Just throw a nice exception because
    CMakeCache.txt was not found.

    """
    mess  = """
    Could not find CMakeCache.txt for project {project.name}.
    (Looked in {project.build_directory})
    """
    if self.active_config:
        mess += "Try using `qibuild configure -c %s {project.name}'" % self.active_config
    else:
        mess += "Try using `qibuild configure {project.name}'"

    mess = mess.format(project=project)

    raise TocException(mess)


def handle_old_qibuild_cfg(worktree):
    """ Handle processing a qibuild.cfg file,
    transforming it to a qibuild.xml file on the fly

    """
    qibuild_xml = os.path.join(worktree, ".qi", "qibuild.xml")
    if not os.path.exists(qibuild_xml):
        qibuild_cfg = os.path.join(worktree, ".qi", "qibuild.cfg")
        if os.path.exists(qibuild_cfg):
            xml = qibuild.config.convert_qibuild_cfg(qibuild_cfg)
            with open(qibuild_xml, "w") as fp:
                fp.write(xml)

def handle_old_qibuild_xml(worktree):
    """ Handle processing an old qibuild.xml  file,
    creating the global xml config on the fly if it does not
    exist

    """
    global_path = qibuild.config.QIBUILD_CFG_PATH
    from xml.etree import ElementTree as etree
    local_xml_path = os.path.join(worktree, ".qi", "qibuild.xml")
    tree = etree.ElementTree()
    tree.parse(local_xml_path)
    qibuild_tree = tree.getroot()
    if qibuild_tree.get("version") == "1" and os.path.exists(global_path):
        return
    (global_xml, local_xml) = qibuild.config.convert_qibuild_xml(local_xml_path)
    with open(local_xml_path, "w") as fp:
        fp.write(local_xml)
    if os.path.exists(global_path):
        # Refuse to try to merge back global configs ...
        # FIXME: add an error message here?
        return
    qibuild.sh.mkdir(os.path.dirname(global_path), recursive=True)
    with open(global_path, "w") as fp:
        fp.write(global_xml)

