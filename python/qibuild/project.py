## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import argparse
import copy
import json
import os
import platform
import re
import sys
from xml.etree import ElementTree as etree

from qisys import ui
import qisys.command
import qisys.error
import qisys.parsers
import qisys.sh
import qibuild
import qibuild.cmake
import qibuild.build
import qibuild.breakpad
import qibuild.gcov
import qibuild.gdb
import qibuild.dylibs
import qibuild.dlls
import qibuild.test_runner
import qisrc.worktree
import qisrc.git
import qitoolchain.toolchain
import qitest.conf
import qitest.project


def read_install_manifest(filepath):
    with open(filepath, "r") as f:
        res = [filename.strip() for filename in f.readlines()]
        res = [qisys.sh.to_posix_path(x) for x in res]
        res = [x.lstrip("/") for x in res]
        return res

def write_qi_path_conf(sdk_directory, sdk_dirs):
    """ Write the <build>/sdk/share/qi/path.conf file. This file
    can be used for instance by qi::path::find() functions, to
    find files from the dependencies' build directory

    """
    to_write = ""
    for sdk_dir in sdk_dirs:
        to_write += qisys.sh.to_native_path(sdk_dir) + "\n"

    path_dconf = os.path.join(sdk_directory, "share", "qi")
    qisys.sh.mkdir(path_dconf, recursive=True)

    path_conf = os.path.join(path_dconf, "path.conf")
    with open(path_conf, "w") as fp:
        fp.write(to_write)


class BuildProject(object):
    def __init__(self, build_worktree, worktree_project):
        self.build_worktree = build_worktree
        self.worktree_project = worktree_project
        self.path = worktree_project.path
        self.src = worktree_project.src
        self._name = None
        self.version = self.worktree_project.version
        # depends is a set at this point because they are not sorted yet
        self.build_depends = set()
        self.run_depends = set()
        self.test_depends = set()
        self.host_depends = set()
        self.meta = False

    @property
    def name(self):
        return self._name

    @property
    def build_config(self):
        return self.build_worktree.build_config

    @name.setter
    def name(self, value):
        ui.valid_filename(value)
        self._name = value

    @property
    def license(self):
        return self.worktree_project.license

    @license.setter
    def license(self, value):
        self.worktree_project.license = value

    @property
    def qiproject_xml(self):
        """ Path to qiproject.xml """
        return os.path.join(self.path, "qiproject.xml")

    @property
    def build_directory(self):
        """ Return a suitable build directory, depending on the
        build setting of the worktree: the build config, and
        whether or not a build prefix is set

        """
        return self._get_build_directory()

    def _get_build_directory(self, name=None, system=False):
        build_directory_name = self.build_config.build_directory(name=name, system=system)
        build_prefix = self.build_config.build_prefix
        if build_prefix:
            return os.path.join(self.build_worktree.root,
                                build_prefix,
                                build_directory_name,
                                self.name)
        else:
            return os.path.join(self.path, build_directory_name)

    @property
    def cmake_cache(self):
        return os.path.join(self.build_directory, "CMakeCache.txt")

    @property
    def qitest_json(self):
        return os.path.join(self.sdk_directory, "qitest.json")

    @property
    def cmake_args(self):
        """ The list of CMake arguments to use when configuring the
        project.
        Delegates to build_config.cmake_args

        """
        return self.build_config.cmake_args

    @property
    def build_env(self):
        """ The environment to use when calling cmake or build commands

        """
        return self.build_config.build_env

    @property
    def sdk_directory(self):
        """ The sdk directory in the build directory """
        res = os.path.join(self.build_directory, "sdk")
        return res

    @property
    def cmake_generator(self):
        return qibuild.cmake.get_cached_var(self.build_directory, "CMAKE_GENERATOR")

    @property
    def build_type(self):
        if self.meta:
            return None
        default = self.build_config.build_type
        return qibuild.cmake.get_cached_var(self.build_directory,
                                            "CMAKE_BUILD_TYPE",
                                             default=default)

    @property
    def toolchain(self):
        return self.build_config.toolchain

    @property
    def using_visual_studio(self):
        return self.build_config.using_visual_studio

    @property
    def using_make(self):
        return self.build_config.using_make

    @property
    def verbose_make(self):
        return self.build_config.verbose_make

    def write_dependencies_cmake(self, sdk_dirs, host_dirs=None):
        """ Write the dependencies.cmake file. This will be read by
        qibuild-config.cmake to set CMAKE_PREFIX_PATH and
        qibuild_DIR, so that just running `cmake ..` works

        """
        to_write = """
#############################################
#QIBUILD AUTOGENERATED FILE. DO NOT EDIT.
#############################################

# Add path to CMake framework path if necessary:
set(_qibuild_path "{cmake_qibuild_dir}")
list(FIND CMAKE_MODULE_PATH "${{_qibuild_path}}" _found)
if(_found STREQUAL "-1")
  # Prefer cmake files matching  current qibuild installation
  # over cmake files in the cross-toolchain
  list(INSERT CMAKE_MODULE_PATH 0 "${{_qibuild_path}}")
endif()

# Dependencies:
{dep_to_add}

# Store CMAKE_MODULE_PATH and CMAKE_PREFIX_PATH in cache:
set(CMAKE_MODULE_PATH ${{CMAKE_MODULE_PATH}} CACHE INTERNAL ""  FORCE)
set(CMAKE_PREFIX_PATH ${{CMAKE_PREFIX_PATH}} CACHE INTERNAL ""  FORCE)

{custom_cmake_code}
"""
        custom_cmake_code = ""
        if self.build_config.local_cmake:
            to_include = qisys.sh.to_posix_path(self.build_config.local_cmake)
            custom_cmake_code += 'include("%s")\n' % to_include

        cmake_qibuild_dir = qibuild.cmake.get_cmake_qibuild_dir()
        cmake_qibuild_dir = qisys.sh.to_posix_path(cmake_qibuild_dir)
        dep_to_add = ""
        dirs_to_add = sdk_dirs
        if host_dirs:
            dirs_to_add = host_dirs + sdk_dirs
        for dir_to_add in dirs_to_add:

            dep_to_add += """\
list(FIND CMAKE_PREFIX_PATH "{dir_to_add}" _found)
if(_found STREQUAL "-1")
  list(APPEND CMAKE_PREFIX_PATH "{dir_to_add}")
endif()
""".format(dir_to_add=qisys.sh.to_posix_path(dir_to_add))

        to_write = to_write.format(
            cmake_qibuild_dir=cmake_qibuild_dir,
            dep_to_add=dep_to_add,
            custom_cmake_code=custom_cmake_code
        )

        qibuild_python = os.path.join(qibuild.__file__, "..", "..")
        qibuild_python = os.path.abspath(qibuild_python)
        qibuild_python = qisys.sh.to_posix_path(qibuild_python)
        to_write += """
set(QIBUILD_PYTHON_PATH "%s" CACHE STRING "" FORCE)
""" % qibuild_python


        qisys.sh.mkdir(self.build_directory, recursive=True)
        dep_cmake = os.path.join(self.build_directory, "dependencies.cmake")
        qisys.sh.write_file_if_different(to_write, dep_cmake)

    def bootstrap(self):
        qi_path_sdk_dirs = [p.sdk_directory for p in self.build_worktree.build_projects]
        if self.toolchain:
            qi_path_sdk_dirs.extend(package.path for package in self.toolchain.packages)
        write_qi_path_conf(self.sdk_directory, qi_path_sdk_dirs)

    def configure(self, **kwargs):
        """ Delegate to :py:func:`qibuild.cmake.cmake` """
        # Need a copy because cmake_args will be modified by
        # qibuild.cmake.cmake()
        cmake_args = copy.copy(self.cmake_args)
        qisys.sh.mkdir(self.sdk_directory, recursive=True)
        if kwargs.get("allow_cmake_skip"):
            need_configure = self.need_configure()
        else:
            need_configure = True
        if not need_configure:
            ui.info("CMakeCache.txt already up to date, skipping")
            return
        kwargs.pop("allow_cmake_skip", None)
        # Make DYLD_ variables also available at configure time
        # (Workaround OS X 10.11 not forwarding DYLD_ variables anymore)
        build_env = self.fix_env(self.build_env)
        self.bootstrap()
        try:
            qibuild.cmake.cmake(self.path, self.build_directory,
                                cmake_args, env=build_env, **kwargs)
            self.write_cmake_args(self.cmake_args)
        except qisys.command.CommandFailedException as error:
            raise qibuild.build.ConfigureFailed(self, error)
        self.generate_qitest_json()

    def write_cmake_args(self, cmake_args):
        flags_txt = os.path.join(self.build_directory, "cmake_args.txt")
        with open(flags_txt, "w") as fp:
            fp.write("\n".join(cmake_args) + "\n")

    def read_cmake_args(self):
        flags_txt = os.path.join(self.build_directory, "cmake_args.txt")
        if not os.path.exists(flags_txt):
            return list()
        with open(flags_txt, "r") as fp:
            lines = fp.readlines()
            return [x.strip() for x in lines]

    def need_configure(self):
        previous_args = self.read_cmake_args()
        if not previous_args:
            ui.debug("Could not read previous CMake args, re-running CMake")
            # First time we run CMake, or configure failed:
            return True

        if previous_args != self.cmake_args:
            if previous_args:
                # Do not display a message if it's the first time
                # we run CMake
                ui.info("CMake arguments changed, re-running CMake")
            return True

        if not os.path.exists(self.cmake_cache):
            ui.debug("CMakeCache.txt does not exist, re-running CMake")
            return True

        def cmake_filter(filename=None, dirname=None):
            """ Return True if cmake should re-run when
            the file has changed

            """
            if dirname:
                # Don't descend into hidden folders
                if dirname.startswith("."):
                    return False
                # Don't descend into build dirs:
                if dirname.startswith("build-"):
                    return False

            if filename:
                # Only consider CMakeLists.txt, qiproject.xml,
                # and .cmake files
                basename = os.path.basename(filename)
                if basename in ["CMakeLists.txt", "qiproject.xml"]:
                    return True
                if basename.endswith(".cmake"):
                    return True

        cmake_cache_time = os.path.getmtime(self.cmake_cache)
        filenames = qisys.sh.ls_r(self.path, filter_fun=cmake_filter)
        for filename in filenames:
            full_path = os.path.join(self.path, filename)
            if os.path.getmtime(full_path) > cmake_cache_time:
                rel_path = os.path.relpath(full_path, self.path)
                ui.info("Re-running CMake because %s has changed" % rel_path)
                return True

    def generate_qitest_json(self):
        """ The qitest.cmake is written from CMake """
        qitest_cmake_path = os.path.join(self.build_directory, "qitest.cmake")
        tests = list()
        if os.path.exists(qitest_cmake_path):
            with open(qitest_cmake_path, "r") as fp:
                lines = fp.readlines()
        else:
            lines = list()
        parser = argparse.ArgumentParser()
        parser.add_argument("cmd", nargs="+")
        parser.add_argument("--name", required=True)
        parser.add_argument("--gtest", action="store_true",
                            help="Tell qitest this is a test using gtest")
        parser.add_argument("--timeout", type=int)
        parser.add_argument("--nightly", action="store_true")
        parser.add_argument("--perf", action="store_true")
        parser.add_argument("--working-directory")
        parser.add_argument("--env", action="append",
                            dest="environment")
        parser.set_defaults(nightly=False, perf=False)
        def log_error(message, line):
            test_name = line.split(";")[1]
            mess = "Could not parse test options for test: '%s'\n" % test_name
            mess += "Error was: %s" % message
            ui.error(mess)
        for line in lines:
            parser.error = lambda message : log_error(message, line)
            line = line.strip()
            try:
                args = parser.parse_args(args=line.split(";"))
            except SystemExit:
                break
            test = vars(args)
            as_list = test["environment"]
            if as_list:
                test["environment"] = dict(x.split("=") for x in as_list)
            tests.append(test)
        with open(self.qitest_json, "w") as fp:
            json.dump(tests, fp, indent=2)


    def build(self, rebuild=False, target=None,
              coverity=False, env=None):
        """ Build the project """
        timer = ui.timer("make %s" % self.name)
        timer.start()

        cmd = []
        if coverity:
            # So that we raise before creating the coverity directory
            qisys.command.find_program("cov-build", raises=True)
            cov_dir = os.path.join(self.build_directory, "coverity")
            qisys.sh.mkdir(cov_dir)
            cmd += ["cov-build", "--dir", cov_dir]

        cmd += ["cmake", "--build", self.build_directory,
                         "--config", self.build_type]

        if target:
            cmd += ["--target", target]

        if rebuild:
            cmd += ["--clean-first"]
        cmd += [ "--" ]
        cmd += self.parse_num_jobs(self.build_config.num_jobs)

        if not env:
            build_env = self.build_env.copy()
        else:
            build_env = env
        build_env = self.fix_env(build_env)
        if self.verbose_make:
            if self.cmake_generator:
                if "Makefiles" in self.cmake_generator:
                    build_env["VERBOSE"] = "1"
                if self.cmake_generator == "Ninja":
                    cmd.append("-v")
        try:
            qisys.command.call(cmd, env=build_env)
        except qisys.command.CommandFailedException:
            raise qibuild.build.BuildFailed(self)

        timer.stop()
        # We need to call generate_qitest_json() here because
        # `qibuild make` may have caused a re-run of cmake
        self.generate_qitest_json()

    def parse_num_jobs(self, num_jobs, cmake_generator=None):
        """ Convert a number of jobs to a list of cmake args """
        if not cmake_generator:
            cmake_generator = \
                    qibuild.cmake.get_cached_var(self.build_directory, "CMAKE_GENERATOR")
        if num_jobs is None:
            # By default, use the "good" number just like Ninja
            if "Visual Studio" in cmake_generator:
                return ["/maxcpucount"]
            return list()
        if "Unix Makefiles" in cmake_generator or \
            "Ninja" in cmake_generator:
            return ["-j", str(num_jobs)]
        if cmake_generator == "NMake Makefiles":
            mess   = "-j is not supported for %s\n" % cmake_generator
            mess += "On Windows, you can use Jom or Ninja instead to compile "
            mess += "with multiple processors"
            raise qisys.error.Error(mess)
        if cmake_generator == "Xcode" or "JOM" in cmake_generator:
            ui.warning("-j is ignored when used with", cmake_generator)
            return list()
        if "Visual Studio" in cmake_generator:
            return ["/maxcpucount:%i" % num_jobs]
        ui.warning("Unknown generator: %s, ignoring -j option" % cmake_generator)
        return list()


    def install(self, destdir, prefix="/", components=None,
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
        installed = list()
        if components is None:
            components = list()
        # DESTDIR=/tmp/foo and CMAKE_PREFIX="/usr/local" means
        # dest = /tmp/foo/usr/local
        destdir = qisys.sh.to_native_path(destdir)
        build_env = self.build_env.copy()
        build_env["DESTDIR"] = destdir
        # Must make sure prefix is not seen as an absolute path here:
        dest = os.path.join(destdir, prefix[1:])
        dest = qisys.sh.to_native_path(dest)

        cprefix = qibuild.cmake.get_cached_var(self.build_directory,
                                               "CMAKE_INSTALL_PREFIX")
        if cprefix != prefix:
            qibuild.cmake.cmake(self.path, self.build_directory,
                ['-DCMAKE_INSTALL_PREFIX=%s' % prefix],
                clean_first=False,
                env=build_env)
        else:
            mess = "Skipping configuration of project %s\n" % self.name
            mess += "CMAKE_INSTALL_PREFIX is already correct"
            ui.debug(mess)

        # Hack for http://www.cmake.org/Bug/print_bug_page.php?bug_id=13934
        if "Unix Makefiles" in self.cmake_generator:
            self.build(target="preinstall", env=build_env)
        if components:
            for component in components:
                files = self._install_component(destdir, component)
                installed.extend(files)
        else:
            self.build(target="install", env=build_env)
            manifest_path = os.path.join(self.build_directory, "install_manifest.txt")
            installed.extend(read_install_manifest(manifest_path))
        if "test" in components:
            self._install_qitest_json(destdir)

        if split_debug:
            self.split_debug(destdir, file_list=installed)

        return installed

    def _install_component(self, destdir, component):
        build_env = self.build_env.copy()
        build_env["DESTDIR"] = destdir

        cmake_args = list()
        cmake_args += ["-DBUILD_TYPE=%s" % self.build_type]
        cmake_args += ["-DCOMPONENT=%s" % component]
        cmake_args += ["-P", "cmake_install.cmake", "--"]
        ui.debug("Installing", component)
        qisys.command.call(["cmake"] + cmake_args, cwd=self.build_directory,
                            env=build_env)
        manifest_path = os.path.join(self.build_directory, "install_manifest_%s.txt" % component)
        installed = read_install_manifest(manifest_path)
        return installed

    def _install_qitest_json(self, destdir):
        if not os.path.exists(self.qitest_json):
            return
        tests = qitest.conf.parse_tests(self.qitest_json)
        tests = qitest.conf.relocate_tests(self, tests)
        qitest.conf.write_tests(tests, os.path.join(destdir, "qitest.json"), append=True)

    def run_tests(self, **kwargs):
        test_project = self.to_test_project()
        test_runner = qibuild.test_runner.ProjectTestRunner(test_project)
        # Note how we do NOT use the env coming from the build config (in
        # self.build_env()), suitable for running CMake and building,
        # but the env coming from the build worktree, suitable to run the tests
        test_runner.env = self.build_worktree.get_env()
        for key, value in kwargs.iteritems():
            if hasattr(test_runner, key):
                setattr(test_runner, key, value)
        return test_runner.run()

    def to_test_project(self):
        if not os.path.exists(self.qitest_json):
            raise NoQiTestJson()
        res = qitest.project.TestProject(self.qitest_json)
        if not res.tests:
            ui.error("No tests were found in qitest.json.\n" +
                     "Add some in the CMakeLists using " +
                     "qi_add_test() or similar")
        res.name = self.name
        return res

    def fix_shared_libs(self, paths):
        """ Do some magic so that shared libraries from other projects and
        packages from toolchains are found

        Called by CMakeBuilder before building

        :param paths: a list of paths from which to look for dependencies

        """
        if sys.platform == "darwin":
            qibuild.dylibs.fix_dylibs(self.sdk_directory, paths=paths)
        if sys.platform.startswith("win"):
            mingw = self.build_config.using_mingw
            qibuild.dlls.fix_dlls(self.sdk_directory, paths=paths,
                                  mingw=mingw, env=self.build_env)

    def fix_env(self, env):
        if sys.platform == "darwin":
            # some projects run binaries during buildtime, they need this hack
            # to find the toolchain libraries until we use cmake 2.8.12 on mac
            lib_dir = os.path.join(self.sdk_directory, "lib")
            envsetter = qisys.envsetter.EnvSetter(build_env=env)
            envsetter.prepend_directory_to_variable(lib_dir, "DYLD_LIBRARY_PATH")
            envsetter.prepend_directory_to_variable(self.sdk_directory, "DYLD_FRAMEWORK_PATH")
            env = envsetter.get_build_env()
        return env

    def split_debug(self, destdir, file_list):
        """ Split debug symbols after install """
        if self.using_visual_studio:
            qisys.error.Error("split debug not supported on Visual Studio")
        ui.info(ui.green, "Splitting debug symbols from binaries ...")
        tool_paths = dict()
        for name in ["objcopy", "objdump"]:
            tool_path = qibuild.cmake.get_binutil(name,
                                                    build_dir=self.build_directory,
                                                    env=self.build_env)
            tool_paths[name] = tool_path

        missing = [x for x in tool_paths if not tool_paths[x]]
        if missing:
            mess  = """\
Could not split debug symbols from binaries for project {name}.
The following tools were not found: {missing}\
"""
            mess = mess.format(name=self.name, missing = ", ".join(missing))
            ui.warning(mess)
            return
        for filename in file_list:
            full_path = os.path.join(destdir, filename)
            if qibuild.breakpad.is_elf(full_path):
                qibuild.gdb.split_debug(full_path, **tool_paths)

    def get_build_dirs(self, all_configs=False):
        """Return a dictionary containing the build directory list
        for the known and the unknown configurations::

            build_directories = {
                'known_configs' = [],
                'unknown_configs' = [],
            }

        Note: if all_configs if False, then the list of the unknown
        configuration remains empty.

        """
        if not all_configs:
            bdirs = list()
            if os.path.isdir(self.build_directory):
                bdirs.append(self.build_directory)
            return {'known_configs': bdirs, 'unknown_configs': list()}

        # build directory name pattern:
        # 'build-<tc_name>[-<profile>]...[-release]'
        build_names = ["build-sys-%s-%s" % (platform.system().lower(),
                                            platform.machine().lower())]
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(create_if_missing=True)
        config_names = qibuild_cfg.configs.keys()
        build_names.extend(["build-" + x for x in config_names])
        build_prefix = self.build_config.build_prefix
        if build_prefix:
            to_list = os.path.join(build_prefix)
            if os.path.exists(to_list):
                dirs = os.listdir(to_list)
            else:
                dirs = list()
        else:
            dirs = os.listdir(self.path)
        ret = {'known_configs': list(), 'unknown_configs': list()}
        for bdir in dirs:
            if bdir in build_names:
                ret['known_configs'].append(bdir)
            elif bdir.startswith("build-"):
                ret['unknown_configs'].append(bdir)
        for k in ret.keys():
            if build_prefix:
                ret[k] = [os.path.join(build_prefix, x, self.name) for x in ret[k]]
            else:
                ret[k] = [os.path.join(self.path, x) for x in ret[k]]
        return ret

    def get_host_sdk_dir(self):
        qibuild_cfg = qibuild.config.QiBuildConfig()
        qibuild_cfg.read(create_if_missing=True)
        host_config = qibuild_cfg.get_host_config()
        if host_config:
            build_directory = self._get_build_directory(name=host_config)
        else:
            build_directory = self._get_build_directory(system=True)
        return os.path.join(build_directory, "sdk")

    def gen_package_xml(self, output):
        package_xml_root = etree.Element("package")
        package_xml_tree = etree.ElementTree(package_xml_root)
        package_xml_root.set("name", self.name)
        if self.version:
            package_xml_root.set("version", self.version)
        if self.license:
            license_elem = etree.SubElement(package_xml_root, "license")
            license_elem.text = self.license
        qibuild.deps.dump_deps_to_xml(self, package_xml_root)
        self._add_scm_info(package_xml_root)
        qisys.qixml.write(package_xml_tree, output)

    def _add_scm_info(self, package_xml_root):
        worktree = self.build_worktree.worktree
        git_worktree = qisrc.worktree.GitWorkTree(worktree)
        git_projects = git_worktree.git_projects
        parent_git_project = qisys.parsers.find_parent_project(git_projects, self.path)
        if not parent_git_project:
            return
        git = qisrc.git.Git(parent_git_project.path)
        rc, out = git.call("rev-parse", "HEAD", raises=False)
        if rc != 0:
            return
        clone_url = parent_git_project.clone_url
        sha1 = out.strip()
        scm_elem = etree.SubElement(package_xml_root, "scm")
        git_elem = etree.SubElement(scm_elem, "git")
        revision_elem = etree.SubElement(git_elem, "revision")
        revision_elem.text = sha1
        if clone_url:
            url_elem = etree.SubElement(git_elem, "url")
            url_elem.text = clone_url

    def __repr__(self):
        return "<BuildProject %s in %s>" % (self.name, self.src)

    def __eq__(self, other):
        return self.name == other.name and self.src == other.src

    def __ne__(self, other):
        return not (self == other)


class BadProjectConfig(qisys.error.Error):
    pass

class NoQiTestJson(qisys.error.Error):
    def __str__(self):
        return """ Could not find qitest.json. Did you run `qibuild configure` ? """
