## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" This module contains the :py:class:`qibuild.toc.Toc` class.
which is where all the 'magic' happens ....

"""

import os
import sys
import glob
import platform
import signal
import operator

from qisys import ui
import qisys
import qisys.envsetter
import qisys.sh
import qisys.worktree
import qibuild
import qibuild.dlls
import qibuild.dylibs
import qibuild.gdb
import qibuild.project
import qibuild.profile

import qitoolchain

from qisys.command  import CommandFailedException
from qibuild.dependencies_solver import DependenciesSolver


class TocException(Exception):
    """Custom exception.
    Specific exceptions raised by toc are of this type,
    so they can be caught by callers.
    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message

class WrongDefaultException(Exception):
    """ Custom exception.
    Caught only by qibuild init

    """
    def __init__(self, message):
        self._message = message

    def __str__(self):
        return self._message

class NoSuchProfile(Exception):
    """ The profile specified by the user cannot be found """
    def __init__(self, toc, profile_name):
        self.toc = toc
        self.profile_name = profile_name

    def __str__(self):
        qibuild_xml = self.toc.config_path
        profiles = qibuild.profile.parse_profiles(qibuild_xml)
        return """ Could not find profile {name}.
Known profiles are: {profiles}
Please check your worktree configuration in:
{qibuild_xml} \
""".format(name=self.profile_name, qibuild_xml=qibuild_xml,
           profiles=', '.join(sorted(profiles.keys())))


class ConfigureFailed(Exception):
    def __init__(self, project, message=None):
        self.project = project
        self.message = message
    def __str__(self):
        res = "Error occured when configuring project %s" % self.project.name
        if self.message:
            res += "\n" + self.message
        return res

class BuildFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when building project %s" % self.project.name

class TestsFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        res  = "Error occured when testing project %s\n" % self.project.name
        return res

class InstallFailed(Exception):
    def __init__(self, project):
        self.project = project
    def __str__(self):
        return "Error occured when installing project %s" % self.project.name


class Toc:
    """
    Example of use:

    .. code-block:: python

        worktree = qisys.worktree.open_worktree("/path/to/src")
        toc = Toc(worktree=worktree, build_type="release")

        # Look for the foo project in the worktree
        foo = toc.get_project("foo")

        # Resolve foo dependencies, call cmake on each of them,
        toc.configure_project(foo)

        # Build the foo project, building all the dependencies in
        # the correct order:
        toc.build_project(foo)

    """
    def __init__(self, worktree,
            config=None,
            qibuild_cfg=None,
            build_type="Debug",
            cmake_flags=None,
            profiles=None,
            cmake_generator=None):
        """
        Create a new Toc object. Most of the keyargs come directly from
        the command line. (--worktree, --debug, -c, etc.)

        :param worktree:  see :py:meth:`qisys.worktree.WorkTree.__init__`
        :param qibuild_cfg: a  :py:class:`qibuild.config.QiBuildConfig` instance
                            if not given, a new one will be created
        :param build_type: a build type, could be debug or release
                           (defaults to debug)
        :param cmake_flags:     optional additional cmake flags
        :param cmake_generator: optional cmake generator
                         (defaults to Unix Makefiles)
        """
        # Set during qibuild.cmdparse.projects_from_args and
        # used by get_sdk_dirs().
        # Why? Assume you have hello depending on world, which is both
        # a project and a pacakge.
        # qc hello  -> get_sdk_dirs('hello') = []
        # qc world hello -> get_sdk_dirs('hello') = ["world/build/sdk"]
        self.active_projects = list()
        self.worktree = worktree
        self.cmake_generator   = cmake_generator
        self.build_type = build_type if build_type else "Debug"
        # List of objects of type qibuild.project.Project,
        # this is updated using WorkTree.buildable_projects
        self.projects          = list()

        # The local config file in which to write
        qisys.sh.mkdir(worktree.dot_qi)

        # Perform format conversion if necessary
        self.config_path = worktree.qibuild_xml
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as fp:
                fp.write("<qibuild />\n")

        handle_old_qibuild_xml(self.worktree.root)
        # Handle config:
        if not qibuild_cfg:
            self.config = qibuild.config.QiBuildConfig(config)
            self.config.read()
        else:
            self.config = config
        self.config.read_local_config(self.config_path)
        self.active_config = self.config.active_config
        # Special case if "--system" was used:
        if config == "system":
            self.active_config = None

        self.local_cmake = None
        if self.active_config:
            local_dir = worktree.dot_qi
            local_cmake = os.path.join(local_dir,
                                       "%s.cmake" % self.active_config)
            if os.path.exists(local_cmake):
                self.local_cmake = local_cmake

        # Set build environment
        envsetter = qisys.envsetter.EnvSetter()
        envsetter.read_config(self.config)
        self.build_env =  envsetter.get_build_env()

        # Set cmake generator if user has not set it in Toc ctor:
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
                local_dir = self.worktree.dot_qi
                local_cmake = os.path.join(local_dir, "%s.cmake" % self.active_config)
                if not os.path.exists(local_cmake):
                    mess  = """Invalid configuration {active_config}
 * No toolchain named {active_config}. Known toolchains are:
    {tc_names}
 * No custom cmake file for config {active_config} found.
   (looked in {local_cmake})
"""
                    mess =  mess.format(active_config=self.active_config,
                                local_cmake = local_cmake,
                                tc_names = qitoolchain.get_tc_names())
                    if self.active_config == self.config.local.defaults.config:
                        mess += """Note: this is your default config
You may want to run:

  qibuild init --force -w {worktree.root}
(to re-initialize your worktree and not use any toolchain)

  qibuild init --force -w {worktree.root} --config=<config>
(to use a different toolchain by default)
 """
                        mess = mess.format(worktree=self.worktree)
                        raise WrongDefaultException(mess)
                    else:
                        raise Exception(mess)
        if self.toolchain:
            self.packages = self.toolchain.packages
        else:
            self.packages = list()

        # Useful vars to cope with Visual Studio quirks
        self.using_visual_studio = "Visual Studio" in self.cmake_generator
        self.vc_version = self.cmake_generator.split()[-1]

        # The actual list of cmake flags we are going to use
        # will be computed during self.update_projects
        # Right now, we will just store the flags passed in ctor
        # in self.user_cmake_flags, to be sure they are always added
        # at the end of the list of flags
        if cmake_flags:
            self.user_cmake_flags = cmake_flags[:]
        else:
            self.user_cmake_flags = list()

        self.profiles = list()
        self.apply_profiles(profiles)

        # Finally, update the build configuration of all the projects
        # (this way we are sure that the build configuration is the same for
        # every project)
        self.update_projects()

    def apply_profiles(self, profile_names):
        """ Apply a profile, adding cmake flags coming from -p command
        line arguments.

        """
        if not profile_names:
            return
        cmake_flags = list()
        profiles = qibuild.profile.parse_profiles(self.config_path)
        for profile_name in profile_names:
            match = profiles.get(profile_name)
            if not match:
                raise NoSuchProfile(self, profile_name)
            else:
                cmake_flags.extend(match.cmake_flags)
                self.profiles.append(profile_name)

        # Re-add custom CMake flags (comfing from -D arguments) at the end:
        self.user_cmake_flags = cmake_flags + self.user_cmake_flags

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
        seen = dict()

        # self.buildable_projects has been set by WorkTree.__init__
        for build_project in qibuild.project.build_projects(self.worktree):
            # Promote the simple worktree project (just a name an a src dir),
            # inside a full qibuild.project.Project object
            # (with CMake flags, build dir, et al.)
            project_path = build_project.path
            qibuild_project = qibuild.project.Project(self, project_path)
            project_name = qibuild_project.name
            if project_name in seen:
                mess  = "Found two qibuild projects with the same name (%s)\n" % qibuild_project.name
                mess += "  * in %s\n" % seen[qibuild_project.name]
                mess += "  * in %s\n" % project_path
                raise Exception(mess)
            self.projects.append(qibuild_project)
            seen[project_name] = project_path

        # Small warning here: when we update the projects, we do NOT
        # have the complete list of the projects, their dependencies,
        # the list of sdk dirs, and so on ...
        # So we only call qibuild.projects.bootstrap_project() at the last
        # moment...
        for project in self.projects:
            qibuild.project.update_project(project, self)

        self.projects.sort(key=operator.attrgetter('name'))


    def get_build_folder_name(self):
        """Get a reasonable build folder.
        The point is to be sure we don't have two incompatible build configurations
        using the same build dir.

        Return a string looking like
        build-linux-release
        build-cross-debug ...
        """
        build_dir = qibuild.toc.get_build_folder_name(config=self.active_config,
                profiles=self.profiles, build_type=self.build_type,
                visual_studio=self.using_visual_studio)
        return build_dir

    def has_project(self, project_name):
        """Return if we can found project_name in the toc projects."""
        known_project_names = (p.name for p in self.projects)

        return project_name in known_project_names

    def get_project(self, project_name, raises=True):
        """ Get a project from a name.

        :return: A valid :py:class:`qibuild.project.Project` instance
        :raise: a TocException if the project was not found

        """
        res = [p for p in self.projects if p.name == project_name]
        if len(res) == 1:
            return res[0]
        if raises:
            raise TocException("No such project: %s" % project_name)
        else:
            return None

    def get_package(self, package_name, raises=True):
        """
        :return: A valid :py:class:`qitoolchain.toolchain.Package` instance
        :raise: a TocException if the project was not found

        """
        res = [p for p in self.packages if p.name == package_name]
        if len(res) == 1:
            return res[0]
        if raises:
            raise TocException("No such package: %s" % package_name)
        return None

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
        if not self.has_project(project_name):
            raise TocException("%s is not a buildable project" % project_name)

        dep_solver = DependenciesSolver(projects=self.projects, packages=self.packages,
            active_projects=self.active_projects)
        (r_project_names, _, not_found) = dep_solver.solve([project_name])

        # Nothing to do with with the packages:
        # SDK dirs from toolchain are managed by the toolchain file in
        # self.toolchain

        if not_found:
            # FIXME: right now there are tons of case where you could have missing
            # projects. (using a cross-toolchain, or an Aldebaran SDK)
            # Put this back later.
            # ui.warning("Could not find projects", ", ".join(not_found))
            pass

        # Remove self from the list:
        r_project_names.remove(project_name)

        dirs = [self.get_project(x).sdk_directory for x in r_project_names]

        ui.debug("sdk_dirs for", project_name, ":", " ".join(dirs))
        return dirs


    def configure_project(self, project, clean_first=True,
                         trace_cmake=False, debug_trycompile=False,
                         coverage=False, profiling=False):
        """ Call cmake with correct options.

        :param clean_first: If False, do not delete CMake cache.
            This is mainly useful when you are calling cmake NOT from
            `qibuild configure`.
        :param debug_trycompile: If True, will pass --debug-trycompile.
            Useful when detecting compiler fails
        :param profiling: If True, will run cmake --trace, and then
            generate some stats.

        """
        timer = ui.timer("configure %s" % project.name)
        timer.start()
        if not os.path.exists(project.path):
            raise TocException("source dir: %s does not exist, aborting" %
                    project.path)
        cmake_file = os.path.join(project.path)
        if not os.path.exists(cmake_file):
            mess = """{project.name} does not look like a valid CMake project!
        (No CMakeLists.txt in {project.path)
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


        cmake_args.extend(["-D" + x for x in cmake_flags])

        if coverage:
            cmake_args.append("-DQI_COVERAGE:BOOL=TRUE")

        if debug_trycompile:
            cmake_args.append("--debug-trycompile")

        if profiling:
            cmake_args.append("--trace")

        if "MinGW" in self.cmake_generator:
            paths = self.build_env["PATH"].split(os.pathsep)
            paths_withoutsh = list()
            for p in paths:
                if not os.path.exists(os.path.join(p, "sh.exe")):
                    paths_withoutsh.append(p)
            self.build_env["PATH"] = os.pathsep.join(paths_withoutsh)

        try:
            qibuild.cmake.cmake(project.path, project.build_directory,
                                cmake_args, env=self.build_env,
                                clean_first=clean_first,
                                debug_trycompile=debug_trycompile,
                                profiling=profiling,
                                trace_cmake=trace_cmake)
            timer.stop()
        except CommandFailedException, e:
            if e.returncode == -signal.SIGSEGV:
                mess = "CMake crashed. "
                mess += "This usually means you have an endless recursive "
                mess += "loop in your cmake code"
            else:
                mess = None
            raise ConfigureFailed(project, message=mess)


    def build_project(self, project, incredibuild=False,
                      num_jobs=1, target=None, rebuild=False,
                      fix_shared_libs=True, verbose_make=False, coverity=False):
        """ Build a project.

        Usually we will simply can ``cmake --build``, but for incredibuild
        we need to call `BuildConsole.exe` with an sln.

        :param fix_shared_libs: Whether we should try to fix the shared
                                libraries so that newly compiled
                                executables can run wihtout setting
                                PATH or LD_LIBRARY_PAT.
                                True by default, but is set to False
                                during `qibuild package` for instance

        """
        timer = ui.timer("make %s" % project.name)
        timer.start()
        check_configure(self, project)
        if fix_shared_libs:
            self.fix_shared_libs(project)

        cmd = []
        if coverity:
            if not qisys.command.find_program("cov-build"):
                raise Exception("cov-build was not found on the system")
            cov_dir = os.path.join(project.build_directory, "coverity")
            qisys.sh.mkdir(cov_dir)
            cmd += ["cov-build", "--dir", cov_dir]

        cmd += ["cmake", "--build", project.build_directory, "--config", self.build_type]

        if target:
            cmd += ["--target", target]

        if rebuild:
            cmd += ["--clean-first"]
        cmd += [ "--" ]
        cmd += num_jobs_to_args(num_jobs, self.cmake_generator)
        if self.using_visual_studio and incredibuild:
            # In order to use incredibuild, we have to do this small hack:
            # (CMake --build will still call devenv.com instead of BuildConsole.exe)
            sln_files = glob.glob(project.build_directory + "/*.sln")
            assert len(sln_files) == 1, "Expecting exactly one sln, got %s" % sln_files
            sln_file = sln_files[0]
            cmd = ["BuildConsole.exe", sln_file]
            cmd += ["/cfg=%s|Win32" % self.build_type]
            cmd += ["/nologo"]
            if target:
                cmd += ["/target=%s" % target]

        make_env = self.build_env.copy()
        if verbose_make:
            if "Makefiles" in self.cmake_generator:
                make_env["VERBOSE"] = "1"
            if self.cmake_generator == "Ninja":
                cmd.append("-v")
        try:
            qisys.command.call(cmd, env=make_env)
        except CommandFailedException:
            raise BuildFailed(project)

        timer.stop()


    def fix_shared_libs(self, project):
        """ Fix shared libraries so that newly compiled
        executables can run withtout having to set any
        environment variable

        """
        (packages, projects) = qibuild.cmdparse.get_deps(self, [project])
        # remove the project given as parameter from the list:
        projects = [p for p in projects if p.name != project.name]
        dep_sdk_dirs = list()
        unique_sdk_dir = self.config.local.build.sdk_dir
        if not unique_sdk_dir:
            dep_sdk_dirs = [x.sdk_directory for x in projects]
        dep_sdk_dirs.extend(p.path for p in packages)
        if sys.platform.startswith("win"):
            mingw = "mingw" in self.cmake_generator.lower()
            qibuild.dlls.fix_dlls(project.sdk_directory, paths=dep_sdk_dirs,
                                  mingw=mingw, build_env=self.build_env)
        if sys.platform == "darwin":
            qibuild.dylibs.fix_dylibs(project.sdk_directory, paths=dep_sdk_dirs)

    def install_project(self, project, destdir, prefix="/",
                        runtime=False, num_jobs=1,
                        split_debug=False):
        """ Install the project

        :param project: project name.
        :param destdir: destination. Note that when using `qibuild install`,
          we will first call `cmake` to make sure `CMAKE_INSTALL_PREFIX` is
          ``/``. But this function simply calls ``cmake --target install``
          in the simple case.
        :param runtime: Whether to install the project as a runtime
           package or not.
           (see :ref:`cmake-install` section for the details)
        :package split_debug: split the debug symbols out of the binaries
            useful for `qibuild deploy`

        """
        # DESTDIR=/tmp/foo and CMAKE_PREFIX="/usr/local" means
        # dest = /tmp/foo/usr/local
        destdir = qisys.sh.to_native_path(destdir)
        self.build_env["DESTDIR"] = destdir
        # Must make sure prefix is not seen as an absolute path here:
        dest = os.path.join(destdir, prefix[1:])
        dest = qisys.sh.to_native_path(dest)

        check_configure(self, project)

        cprefix = qibuild.cmake.get_cached_var(project.build_directory,
                                               "CMAKE_INSTALL_PREFIX")
        if cprefix != prefix:
            qibuild.cmake.cmake(project.path, project.build_directory,
                ['-DCMAKE_INSTALL_PREFIX=%s' % prefix],
                clean_first=False,
                env=self.build_env)
        else:
            mess = "Skipping configuration of project %s\n" % project.name
            mess += "CMAKE_INSTALL_PREFIX is already correct"
            ui.debug(mess)

        if "Unix Makefiles" in self.cmake_generator:
            self.build_project(project, target="preinstall", num_jobs=num_jobs,
                               fix_shared_libs=False)

        if runtime:
            self.install_project_runtime(project, destdir, num_jobs=num_jobs)
        else:
            self.build_project(project, target="install", fix_shared_libs=False)

        if split_debug:
            if self.using_visual_studio:
                raise Exception("split debug not supported on Visual Studio")
            ui.info(ui.green, "Splitting debug symbols from binaries ...")
            tool_paths = dict()
            for name in ["objcopy", "objdump"]:
                tool_path = qibuild.cmake.get_binutil(name,
                                                      build_dir=project.build_directory,
                                                      build_env=self.build_env)
                tool_paths[name] = tool_path

            missing = [x for x in tool_paths if not tool_paths[x]]
            if missing:
                mess  = """\
Could not split debug symbols from binaries for project {project.name}.
The following tools were not found: {missing}\
"""
                mess = mess.format(mess, project=project,
                                   missing = ", ".join(missing))
                ui.warning(mess)
                return
            qibuild.gdb.split_debug(destdir, **tool_paths)

    def install_project_runtime(self, project, destdir, num_jobs=1):
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
            cmake_args += ["-DBUILD_TYPE=%s" % self.build_type]
            cmake_args += ["-DCOMPONENT=%s" % component]
            cmake_args += ["-P", "cmake_install.cmake", "--"]
            cmake_args += num_jobs_to_args(num_jobs, self.cmake_generator)
            ui.debug("Installing", component)
            qisys.command.call(["cmake"] + cmake_args,
                cwd=project.build_directory,
                env=self.build_env,
                )


def toc_open(worktree_root, args=None):
    """ Creates a :py:class:`Toc` object.

    :param worktree: The worktree to be used. (see :py:class:`qisys.worktree.WorkTree`)
    :param args: an ``argparse.NameSpace`` object containing
     the arguments passed from the comand line.

    You should always use this function to call Toc methods from
    a qibuild :term:`action`.

    It takes care of all the options you specify from command line,
    and calls Toc constructor accordingly (see :py:meth:`Toc.__init__`)

    """
    # Note that args can come from:
    #    - a worktree parser
    #    - a toc parser
    #    - a build parser
    # (hence all the hasattr...)
    # ...
    # or simply not given :)

    kwargs = dict()
    for arg in ("config", "profiles", "build_type", "cmake_flags",
                "cmake_generator"):
        if hasattr(args, arg):
            kwargs[arg] = getattr(args, arg)

    worktree = qisys.worktree.open_worktree(worktree_root)
    return Toc(worktree, **kwargs)

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

def advise_using_configure(self, project):
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

def check_configure(toc, project):
    """ Check if we need to run qibuild configure
    before make
    """
    if not project.is_configured():
        advise_using_configure(toc, project)

def handle_old_qibuild_xml(worktree):
    """ Handle processing an old qibuild.xml  file,
    creating the global xml config on the fly if it does not
    exist

    """
    global_path = qibuild.config.get_global_cfg_path()
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
    qisys.sh.mkdir(os.path.dirname(global_path), recursive=True)
    with open(global_path, "w") as fp:
        fp.write(global_xml)

def get_build_folder_name(config=None, profiles=None, build_type=None,
                          visual_studio=False):
    """Get a build folder name from a config, profiles and a build_type."""
    res = list()

    if config:
        res.append(config)
    else:
        res.append("sys-%s-%s" % (platform.system().lower(),
                                                    platform.machine().lower()))

    if profiles:
        res.extend(profiles)

    if not visual_studio:
        # When using cmake + visual studio, sharing the same build dir with
        # several build config is mandatory.
        # Otherwise, it's not a good idea, so we always specify it
        # when it's not "Debug" (the default)
        if build_type and build_type != "Debug":
            res.append(build_type.lower())

    build_dir = '-'.join(res)
    return build_dir
