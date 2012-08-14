## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
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

from qibuild import ui
import qisrc
import qibuild
import qibuild.gdb
import qitoolchain

from qibuild.project  import Project
from qisrc.worktree import WorkTree
from qibuild.command  import CommandFailedException
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

        worktree = qisrc.open_worktree("/path/to/src")
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
            cmake_generator=None,
            active_projects=None,
            solve_deps=True):
        """
        Create a new Toc object. Most of the keyargs come directly from
        the command line. (--worktree, --debug, -c, etc.)

        :param worktree:  see :py:meth:`qisrc.worktree.WorkTree.__init__`
        :param qibuild_cfg: a  :py:class:`qibuild.config.QiBuildConfig` instance
                            if not given, a new one will be created
        :param build_type: a build type, could be debug or release
                           (defaults to debug)
        :param cmake_flags:     optional additional cmake flags
        :param cmake_generator: optional cmake generator
                         (defaults to Unix Makefiles)
        :param active_projects: the projects excplicitely specified by user
        """
        self.worktree = worktree
        # The local config file in which to write
        dot_qi = os.path.join(self.worktree.root, ".qi")
        qibuild.sh.mkdir(dot_qi)
        self.config_path =  os.path.join(dot_qi, "qibuild.xml")
        if not os.path.exists(self.config_path):
            with open(self.config_path, "w") as fp:
                fp.write("<qibuild />\n")

        # Perform format conversion if necessary
        handle_old_qibuild_cfg(self.worktree.root)
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

        self.build_type = build_type
        if not self.build_type:
            self.build_type = "Debug"

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
                local_dir = os.path.join(self.worktree.root, ".qi")
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
        seen = dict()

        # self.buildable_projects has been set by WorkTree.__init__
        for worktree_project in self.worktree.buildable_projects:
            # Promote the simple worktree project (just a name an a src dir),
            # inside a full qibuild.project.Project object
            # (with CMake flags, build dir, et al.)
            project_path = worktree_project.path
            qibuild_project = qibuild.project.Project(project_path)
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

        if not self.using_visual_studio and self.build_type != "Debug":
            # When using cmake + visual studio, sharing the same build dir with
            # several build config is mandatory.
            # Otherwise, it's not a good idea, so we always specify it
            # when it's not "Debug" (the default)
            res.append(self.build_type.lower())

        self.build_folder_name = "-".join(res)

    def get_project(self, project_name, raises=True):
        """ Get a project from a name.

        :return: A vali :py:class:`qibuild.project.Project` instance
        :raise: a TocException if the project was not found

        """
        res = [p for p in self.projects if p.name == project_name]
        if len(res) == 1:
            return res[0]
        if raises:
            raise TocException("No such project: %s" % project_name)
        else:
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
            # ui.warning("Could not find projects", ", ".join(not_found))
            pass

        # Remove self from the list:
        r_project_names.remove(project_name)


        for project_name in r_project_names:
            project = self.get_project(project_name)
            dirs.append(project.get_sdk_dir())

        ui.debug("sdk_dirs for", project_name, ":", " ".join(dirs))
        return dirs


    def resolve_deps(self, runtime=False):
        """ Return a tuple of three lists:
        (projects, packages, not_foud), see :py:mod:`qibuild.dependencies_solver`
        for more information.

        Note that the result depends on how the Toc object has been built.

        For instance, assuming you have 'hello' depending on 'world', and
        'world' is also a package, you will get:

        (['hello'], ['world'], [])  if user used

        .. code-block:: console

           $ qibuild configure hello

        but:

        (['world', 'hello], [], []) if user used:

        .. code-block:: console

           $ qibuild configure world hello

        """
        if not self.solve_deps:
            return (self.active_projects, list(), list())
        else:
            dep_solver = DependenciesSolver(projects=self.projects,
                                            packages=self.packages,
                                            active_projects=self.active_projects)
            return dep_solver.solve(self.active_projects,
                                    runtime=runtime)

    def configure_project(self, project,
        clean_first=True,
        debug_trycompile=False):
        """ Call cmake with correct options.

        :param clean_first: If False, do not delete CMake cache.
            This is mainly useful when you are calling cmake NOT from
            `qibuild configure`.
        :param debug_trycompile: If True, will pass --debug-trycompile.
            Useful when detecting compiler fails

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


        cmake_args.extend(["-D" + x for x in cmake_flags])

        if debug_trycompile:
            cmake_args.append("--debug-trycompile")

        if "MinGW" in self.cmake_generator:
            paths = self.build_env["PATH"].split(os.pathsep)
            paths_withoutsh = list()
            for p in paths:
                if not os.path.exists(os.path.join(p, "sh.exe")):
                    paths_withoutsh.append(p)
            self.build_env["PATH"] = os.pathsep.join(paths_withoutsh)

        try:
            qibuild.cmake.cmake(project.directory,
                          project.build_directory,
                          cmake_args,
                          clean_first=clean_first,
                          env=self.build_env)
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
                      fix_shared_libs=True):
        """ Build a project.

        Usually we will simply can ``cmake --build``, but for incredibuild
        we need to call `BuildConsole.exe` with an sln.

        :param fix_shared_libs: Wether we should try to fix the shared
                                libraries so that newly compiled
                                executables can run wihtout setting
                                PATH or LD_LIBRARY_PAT.
                                True by default, but is set to False
                                during `qibuild package` for instance

        """
        build_dir = project.build_directory
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cmake_cache):
            advise_using_configure(self, project)

        cmd = ["cmake", "--build", build_dir, "--config", self.build_type]
        if target:
            cmd += ["--target", target]

        if rebuild:
            cmd += ["--clean-first"]
        cmd += [ "--" ]
        cmd += num_jobs_to_args(num_jobs, self.cmake_generator)
        if self.using_visual_studio and incredibuild:
            # In order to use incredibuild, we have to do this small hack:
            # (CMake --build will still call devenv.com instead of BuildConsole.exe)
            sln_files = glob.glob(build_dir + "/*.sln")
            assert len(sln_files) == 1, "Expecting only one sln, got %s" % sln_files
            sln_file = sln_files[0]
            cmd = ["BuildConsole.exe", sln_file]
            cmd += ["/cfg=%s|Win32" % self.build_type]
            cmd += ["/nologo"]
            if target:
                cmd += ["/target=%s" % target]
        try:
            qibuild.command.call(cmd, env=self.build_env)
        except CommandFailedException:
            raise BuildFailed(project)

        if fix_shared_libs:
            self.fix_shared_libs(project)


    def fix_shared_libs(self, project):
        """ Fix shared libraries so that newly compiled
        executables can run withtout having to set any
        environment variable

        """
        sdk_dir   = project.sdk_directory

        paths = list()

        for package in self.packages:
            paths.append(package.path)

        sdk_dirs = self.get_sdk_dirs(project.name)
        paths.extend(sdk_dirs)

        if sys.platform.startswith("win"):
            mingw = "mingw" in self.cmake_generator.lower()
            import qibuild.dlls
            qibuild.dlls.fix_dlls(sdk_dir, paths=paths,
                mingw=mingw,
                build_env=self.build_env)
        if sys.platform == "darwin":
            import qibuild.dylibs
            qibuild.dylibs.fix_dylibs(sdk_dir, paths=paths)

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
        build_dir = project.build_directory
        # DESTDIR=/tmp/foo and CMAKE_PREFIX="/usr/local" means
        # dest = /tmp/foo/usr/local
        destdir = qibuild.sh.to_native_path(destdir)
        self.build_env["DESTDIR"] = destdir
        # Must make sure prefix is not seen as an absolute path here:
        dest = os.path.join(destdir, prefix[1:])
        dest = qibuild.sh.to_native_path(dest)
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        if not os.path.exists(cmake_cache):
            mess  = """Could not install project {project.name}
It appears the project has not been configured.
({cmake_cache} does not exist)
Try configuring and building the project first.
"""
            mess = mess.format(config=self.active_config,
                project=project, cmake_cache=cmake_cache)
            raise Exception(mess)

        cprefix = qibuild.cmake.get_cached_var(build_dir, "CMAKE_INSTALL_PREFIX")
        if cprefix != prefix:
            qibuild.cmake.cmake(project.directory, project.build_directory,
                ['-DCMAKE_INSTALL_PREFIX=%s' % prefix],
                clean_first=False,
                env=self.build_env)
        else:
            mess = "Skipping configuration of project %s\n" % project.name
            mess += "CMAKE_INSTALL_PREFIX is already correct"
            ui.debug(mess)

        if not self.using_visual_studio and not self.cmake_generator == "Xcode":
            self.build_project(project, target="preinstall", num_jobs=num_jobs,
                               fix_shared_libs=False)

        if runtime:
            self.install_project_runtime(project, destdir, num_jobs=num_jobs)
        else:
            self.build_project(project, target="install", fix_shared_libs=False)

        if split_debug:
            if self.using_visual_studio:
                raise Exception("split debug not supported on Visual Studio")
            objcopy = qibuild.cmake.get_cached_var(project.build_directory, "CMAKE_OBJCOPY")
            if objcopy is None:
                objcopy = qibuild.command.find_program("objcopy", env=self.build_env)

            if not objcopy:
                mess  = """\
Could not split debug symbols from binaries for project {project.name}.
Could not find objcopy executable.\
"""
                qibuild.ui.warning(mess.format(project=project))
            else:
                qibuild.gdb.split_debug(destdir, objcopy=objcopy)

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
            cmake_args += ["-DCOMPONENT=%s" % component]
            cmake_args += ["-P", "cmake_install.cmake", "--"]
            cmake_args += num_jobs_to_args(num_jobs, self.cmake_generator)
            ui.debug("Installing", component)
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
        ui.debug("select: All projects have been selected")
        return (toc_p_names, False)

    if hasattr(args, "projects"):
        if args.projects:
            ui.debug("select: projects list from arguments: %s", ",".join(args.projects))
            return ([args.projects, args.single])
        else:
            from_cwd = None
            try:
                from_cwd = qibuild.project.project_from_cwd()
            except:
                pass
            if from_cwd:
                ui.debug("select: projects from cwd: %s", from_cwd)
                return ([from_cwd], args.single)
            else:
                ui.debug("select: default to all projects")
                return (toc_p_names, args.single)
    else:
        return (list(), False)


def toc_open(worktree_root, args=None, qibuild_cfg=None):
    """ Creates a :py:class:`Toc` object.

    :param worktree: The worktree to be used. (see :py:class:`qisrc.worktree.WorkTree`)
    :param args: an ``argparse.NameSpace`` object containing
     the arguments passed from the comand line.
    :param qibuild_cfg: A (:py:class:`qibuild.config.QiBuildConfig` instance) to use.
     If None, we built a new instance to store in ``toc.config``

    You should always use this function to call Toc methods from
    a qibuild :term:`action`.

    It takes care of all the options you specify from command line,
    and calls Toc constructor accordingly (see :py:meth:`Toc.__init__`)

    """
    # Not that args can come from:
    #    - a worktree parser
    #    - a toc parser
    #    - a build parser
    # (hence all the hasattr...)
    # ...
    # or simply not given :)

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

    worktree = qisrc.worktree.open_worktree(worktree_root)
    toc = Toc(worktree,
               config=config,
               build_type=build_type,
               cmake_flags=cmake_flags,
               cmake_generator=cmake_generator,
               qibuild_cfg=qibuild_cfg)

    (active_projects, single) =  _projects_from_args(toc, args)
    toc.active_projects = active_projects
    ui.debug("active projects: %s", ".".join(toc.active_projects))
    ui.debug("single: %s", str(single))
    toc.solve_deps = (not single)
    return toc

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
    if "Unix Makefiles" in  cmake_generator:
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

def create(directory, force=False):
    """ Create a new toc worktree inside a work tree

    """
    qisrc.worktree.create(directory, force=force)

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
    qibuild.sh.mkdir(os.path.dirname(global_path), recursive=True)
    with open(global_path, "w") as fp:
        fp.write(global_xml)
