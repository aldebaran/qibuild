## Copyright (C) 2011 Aldebaran Robotics

""" This module contains the Toc class.
which is where all the 'magic' happens ....

"""

import os
import sys
import glob
import platform
import subprocess
import logging
import qibuild.qiworktree

import qibuild
from   qibuild.project     import Project
import qibuild.sh
from qibuild.dependencies_solver import DependenciesSolver
from   qibuild.qiworktree import QiWorkTree
import qitoolchain
from qibuild.command import CommandFailedException

LOGGER = logging.getLogger("qibuild.toc")


class BadBuildConfig(Exception):
    """Custom exception"""
    def __init__(self, message):
        self.message = message

    def __str__(self):
        mess = self.message + "\n"
        mess += "Please check qi configuration"
        return mess

class TocException(Exception):
    """Custom exception.
    Specific exceptions raised by toc are of this type,
    so they can be caught by callers.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message

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
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when testing project %s" % self.project.name

class InstallFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when installing project %s" % self.project.name

class TocConfigStore:
    """ A configuration associated with a Toc object..

    Pass a toc Object to its constructor, and optionnaly
    a custom config to use, then use get() as you would do
    for a ConfigStore object, the setting from the
    [general]  and  [config '...'] sections will be merged
    for you.

    """
    def __init__(self, toc, user_config=None):

        # A internal configstore object
        self._configstore = qibuild.configstore.ConfigStore()

        # Read from config files
        self.default_config = None

        # The config that is being used
        self.active_config = None

        self.toc = toc
        self._load_config()
        if user_config:
            self.active_config = user_config
        else:
            self.active_config = self.default_config

    def _load_config(self):
        """ Initialize the configstore attribute,
        and the default configuration.

        """
        general_file = qibuild.configstore.get_config_path()
        self._configstore.read(general_file)

        local_file = os.path.join(self.toc.work_tree, ".qi", "qibuild.cfg")
        self._configstore.read(local_file)

        self.default_config = self._configstore.get('general', 'config')

    def get(self, *args, **kwargs):
        """ Handle different configurations, for instance, assuming the
        configuration looks like:

          [general]
          build.cmake.flags = FOO=BAR
          config = mingw32

          [config vs2010]
          build.cmake.generator = 'Visual Studio 10'

          [config mingw32]
          build.cmake.generator = 'MinGW Makefiles'
          env.path = c:\MinGW\bin;

        and self.config = 'vs2010'
        self.get('build, 'cmake', 'generator')
        returns 'Visual Studio 10',

        whereas
        self.get('build', 'cmake', 'flags')
        returns 'FOO=BAR'

        """
        default = kwargs.get('default')
        res = self._configstore.get('config', self.active_config, *args)
        if not res:
            res = self._configstore.get('general', *args)

        if not res:
            res = default

        return res

    def __str__(self):
        return str(self._configstore)



class Toc(QiWorkTree):
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
            cmake_generator=None):
        """
            work_tree       : see QiWorkTree.__init__
            path_hints      : see QiWorkTree.__init__

            build_type      : a build type, could be debug or release (defaults to debug)
            cmake_flags     : optional additional cmake flags
            cmake_generator : optional cmake generator (defaults to Unix Makefiles)
        """
        QiWorkTree.__init__(self, work_tree, path_hints=path_hints)

        # User set a configuration, use it, then build
        # the configstore
        self.configstore = TocConfigStore(self, config)
        if config:
            self.active_config = config
        else:
            self.active_config = self.configstore.default_config

        self.build_type        = build_type

        # The cmake flags set by the user will always be added
        # to the actual cmake flags used by the Toc oject,
        # but we may add other flags when using a toolchain.
        # see self.update_cmake_flags()
        self.cmake_flags       = list()
        self.cmake_generator   = cmake_generator
        self.build_folder_name = None

        # Set build environment
        self.set_build_env()

        # List of objects of type qibuild.project.Project,
        # this is updated using QiWorkTree.buildable_projects
        self.projects          = list()

        # Set cmake generator
        if not self.cmake_generator:
            self.cmake_generator = self.configstore.get("cmake.generator", default="Unix Makefiles")

        # Read the current config, create toolchain and pacakges object
        # if necessary
        self.packages = list()
        self.toolchain = None
        if self.active_config is not None:
            if self.active_config in qitoolchain.get_toolchain_names():
                self.toolchain = qitoolchain.Toolchain(self.active_config)
                self.packages  = self.toolchain.packages
            else:
                # The config does not match a toolchain (but who knows,
                # this may be only some cmake flags in a specific section
                # for instance :
                #   [config perf]
                #   cmake.flags = WITH_TEST=OFF WITH_PERF=ON
                pass

        # Useful vars to cope with Visual Studio quirks
        self.using_visual_studio = "Visual Studio" in self.cmake_generator
        self.vc_version = self.cmake_generator.split()[-1]

        # Actual list of cmake flags we are going to use.
        # * the toolchain file if a toolchain is used
        # * additional cmake flags from the *.cmake config files
        # * and the flags set by the user.
        self.cmake_flags = self.compute_cmake_flags(cmake_flags)

        # Finally, update the build configuration of all the projects
        # (this way we are sure that the build configuration is the same for
        # every project)
        self.update_projects()



    def update_projects(self):
        """Set self.projects() with the correct build configs and correct build folder
        name.

        This make sure that every project managed by a Toc instance has the correct
        build config, and the same build folder

        """
        self.set_build_folder_name()

        # self.buildable_projects has been set by QiWorkTree.__init__
        for pname, ppath in self.buildable_projects.iteritems():
            project = Project(pname, ppath)
            project.update_build_config(self, self.build_folder_name)
            self.projects.append(project)


    def compute_cmake_flags(self, user_flags):
        """ The cmake flags used by toc comes for several source:
        - if a toolchain is used, add
           -DCMAKE_TOOLCHAIN_FILE = toolchain.toolchain_file
        - if ~/.config/qi/<tc_name>.cmake exist, parse the file and add flags
        - same thing for ~/.qi/<tc_name>.cmake

        Finally, add user_cmake_flags (which are the flags set by the user,
        passed to Toc ctor.

        """
        if not self.toolchain:
            if user_flags:
                return user_flags
            else:
                return list()

        res = list()
        tc_file = self.toolchain.toolchain_file
        tc_name = self.toolchain.name
        tc_file = qibuild.sh.to_posix_path(tc_file)
        res.append("CMAKE_TOOLCHAIN_FILE=%s" % tc_file)

        global_cmake = os.path.join(qibuild.configstore.get_config_dir(),
            "%s.cmake" % tc_name)
        if os.path.exists(global_cmake):
            to_add = qibuild.parse_cmake(global_cmake)
            LOGGER.debug("Adding flags from %s : %s", global_cmake, ", ".join(to_add))
            res.extend(to_add)

        local_cmake = os.path.join(self.work_tree, ".qi", "%s.cmake" % tc_name)
        if os.path.exists(local_cmake):
            to_add = qibuild.parse_cmake(local_cmake)
            LOGGER.debug("Adding flags from %s : %s", local_cmake, ", ".join(to_add))
            res.extend(to_add)

        if user_flags:
            res.extend(user_flags)

        return res


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
        """ Return a list of sdk, needed to build a project.

        Iterate through the dependencies.
        When it is a package (pre-compiled), add the path of
        the package, when it is a project, add the path to the "sdk" dir
        under the build directory of the project.

        """
        dirs = list()

        known_project_names = [p.name for p in self.projects]
        if project_name not in known_project_names:
            raise TocException("%s is not a buildable project" % project_name)

        dep_solver = DependenciesSolver(projects=self.projects, packages=self.packages)
        (project_names, package_names, not_found) = dep_solver.solve([project_name])

        if not_found:
            if self.toolchain is None or self.toolchain.cross:
                LOGGER.warning("Could not find projects %s", ", ".join(not_found))

        project_names.remove(project_name)

        # SDK_DIRS from toolchain are managed inside the toolchain.cmake file
        # of the toolchain

        for project_name in project_names:
            project = self.get_project(project_name)
            dirs.append(project.get_sdk_dir())

        LOGGER.debug("sdk_dirs for %s : %s", project_name, dirs)
        return dirs


    def set_build_env(self):
        """Update os.environ using the qibuild configuration file

        """
        env = self.configstore.get("env")
        path = None
        bat_file = None
        if env:
            path = env.get("path")
            bat_file = env.get("bat_file")
        if path:
            self._set_env_from_path_conf(path)
        if bat_file:
            self._set_path_from_bat_conf(bat_file)

    def _set_env_from_path_conf(self, path):
        """Set os.environ using a "path" string setting

        """
        system_path = os.environ["PATH"]
        if not system_path.endswith(os.path.pathsep):
            system_path += os.path.pathsep
        path = path.strip()
        path = path.replace("\n", "")
        LOGGER.debug("adding %s to PATH", path)
        new_path = system_path + path
        os.environ["PATH"] = new_path

    def _set_path_from_bat_conf(self, bat_file):
        """Set environment variables using a .bat script
        """
        # Quick hack to get env vars from a .bat script
        # (stolen idea from distutils/msvccompiler)
        # TODO: handle non asccii chars?
        # Hint: decode("mcbs") ...
        if not os.path.exists(bat_file):
            raise BadBuildConfig("general.env.bat_file (%s) does not exists" % bat_file)

        interesting = set(("INCLUDE", "LIB", "LIBPATH", "PATH"))
        result = {}

        # This call is strange, but necessary.
        # See: http://bytes.com/topic/python/answers/634409-subprocess-handle-invalid-error#post2512502
        popen = subprocess.Popen('"%s"& set' % (bat_file),
                             stdout=subprocess.PIPE,
                             stdin=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             shell=True)


        popen.stdin.close()
        popen.stderr.close()
        out = popen.stdout.read()
        if popen.wait() != 0:
            raise BadBuildConfig("Calling general.env.bat_file failed!")

        for line in out.split("\n"):
            if '=' not in line:
                continue
            line = line.strip()
            key, value = line.split('=', 1)
            key = key.upper()
            if key in interesting:
                if value.endswith(os.pathsep):
                    value = value[:-1]
                result[key] = value

        LOGGER.debug("Updating os.environ with %s" , result)
        os.environ.update(result)


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

        # Set generator if necessary
        cmake_args = list()
        if self.cmake_generator:
            cmake_args.extend(["-G", self.cmake_generator])

        cmake_flags = list()
        cmake_flags.extend(project.cmake_flags)

        cmake_args.extend(["-D" + x for x in cmake_flags])

        if self.toolchain is not None:
            tc_file = self.toolchain.toolchain_file
            toolchain_path = qibuild.sh.to_posix_path(tc_file)
            
        cmake_args.append('-DCMAKE_TOOLCHAIN_FILE=%s' % toolchain_path)


        #remove sh.exe from path on win32, because cmake will fail when using mingw generator.
        env = os.environ.copy()
        if "MinGW" in self.cmake_generator:
            paths = os.environ["PATH"].split(os.pathsep)
            paths_withoutsh = list()
            for p in paths:
                if not os.path.exists(os.path.join(p, "sh.exe")):
                    paths_withoutsh.append(p)
            env["PATH"] = os.pathsep.join(paths_withoutsh)

        try:
            qibuild.cmake(project.directory,
                          project.build_directory,
                          cmake_args,
                          clean_first=clean_first,
                          env=env)
        except CommandFailedException:
            raise ConfigureFailed(project)


    def build_project(self, project, incredibuild=False, num_jobs=1, target=None, rebuild=False):
        """Build a project, choosing between  Nmake, Visual Studio or make

        """
        build_dir = project.build_directory
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cmake_cache):
            _advise_using_configure(project)

        cmd = ["cmake", "--build", build_dir, "--config", self.build_type]
        if target:
            cmd += ["--target", target]

        if rebuild:
            cmd += ["--clean-first"]

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
                if self.vc_version == "10":
                    # CMake will use MSBuild for VS2010 builds, in other
                    # cases, it uses devenv directly
                    cmd = cmd + ["--", "/verbosity:minimal", "/nologo"]
                if num_jobs > 1 and "visual studio" in self.cmake_generator.lower():
                    cmd += ["/m:%d" % num_jobs]

        if num_jobs > 1 and "make" in self.cmake_generator.lower():
            cmd += ["--", "-j%d" % num_jobs]

        try:
            qibuild.command.check_call(cmd)
        except CommandFailedException:
            raise BuildFailed(project)

    def test_project(self, project, verbose_tests=False, test_name=None):
        """Run ctest on a project

        Print the output of the tests in verbose_tests is True
        Only run the test given in test_name is not None
        """
        build_dir = project.build_directory
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cmake_cache):
            _advise_using_configure(project)
        cmd = ["ctest"]
        if verbose_tests:
            cmd.append("-VV")
        if test_name is not None:
            cmd.extend(["-R", test_name])

        try:
            qibuild.command.check_call(cmd, cwd=build_dir)
        except CommandFailedException:
            raise TestsFailed(project)


    def install_project(self, project, destdir, runtime=False):
        """Install the project """
        build_dir = project.build_directory
        build_environ = os.environ.copy()
        build_environ["DESTDIR"] = destdir
        try:
            if runtime:
                self.install_project_runtime(project, destdir)
            else:
                cmd = ["cmake", "--build", build_dir, "--config", self.build_type,
                        "--target", "install"]
                qibuild.command.check_call(cmd, env=build_environ)
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
            build_env = os.environ.copy()
            build_env["DESTDIR"] = destdir
            cmake_args = list()
            cmake_args += ["-DCOMPONENT=%s" % component]
            cmake_args += ["-P", "cmake_install.cmake"]
            LOGGER.debug("Installing %s", component)
            qibuild.command.check_call(["cmake"] + cmake_args,
                cwd=project.build_directory,
                env=build_env)

def toc_open(work_tree, args, use_env=False):
    config   = args.config
    build_type     = args.build_type
    path_hints     = list()
    try:
        cmake_flags = args.cmake_flags
    except:
        cmake_flags = list()

    cmake_generator = args.cmake_generator

    if not work_tree:
        work_tree = qibuild.qiworktree.guess_work_tree(use_env)
    current_project = qibuild.qiworktree.search_current_project_root(os.getcwd())
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
    return Toc(work_tree,
               config=config,
               build_type=build_type,
               cmake_flags=cmake_flags,
               cmake_generator=cmake_generator,
               path_hints=path_hints)


def create(directory, args):
    """ Create a new toc work_tree.

    """
    qibuild.qiworktree.create(directory)


def resolve_deps(toc, args, runtime=False):
    """ To be called from commmand line. (args being the result
    of parsing with a ArgumentParser object for instance)

    Return a tuple of three lists:
    (projects, package, not_foud), see qibuild.dependencies_solver
    for more documentation.

    Cases handled:
      - nothing specified: get the project from the cwd
      - args.single: do not resolve dependencies
      - args.only_deps: only return dependencies
      - args.use_deps: take dependencies into account
    """
    if not args.projects:
        if not project_from_cwd():
            raise Exception("Could not guess project name from the working tree.\n"
                    "Please try from a subdirectory of a project\n"
                    "or specify the name of the project.")
        project_names = [project_from_cwd()]
    else:
        project_names = args.projects
    dep_solver = DependenciesSolver(projects=toc.projects,
                                    packages=toc.packages)
    return dep_solver.solve(project_names,
        single=args.single,
        all=args.all,
        runtime=runtime)

def project_from_cwd():
    """Return a project name from the current working directory

    """
    project_dir = qibuild.qiworktree.search_current_project_root(os.getcwd())
    if not project_dir:
        return None
    return qibuild.project.name_from_directory(project_dir)


def _advise_using_configure(project):
    """Just throw a nice exception because
    CMakeCache.txt was not found.

    """
    mess  = """
    Could not find CMakeCache.txt for project {project.name}.
    (Looked in {project.build_directory})
    """
    cmake_file = os.path.join(project.directory, "CMakeLists.txt")
    if not os.path.exists(cmake_file):
        mess += """
    Note that {project.name} does not look like a valid CMake project
    (No CMakeLists.txt in {project.directory})
    """
    else:
        mess += "Try using `qibuild configure {project.name}'"

    mess = mess.format(project=project)

    raise TocException(mess)
