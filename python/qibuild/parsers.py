## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for qibuild actions
"""

import os

from qisys import ui
import qisys.parsers
import qibuild.worktree
import qibuild.cmake_builder
import qibuild.deps


def cmake_build_parser(parser, group=None, with_build_parser=True):
    if with_build_parser:
        qisys.parsers.build_parser(parser, group=None)
    if not group:
        group = parser.add_argument_group("Build options")
    qisys.parsers.parallel_parser(group, default=None)
    group.add_argument("--verbose-make", action="store_true", default=False,
                    help="Print the executed commands while building")

def cmake_configure_parser(parser):
    group = parser.add_argument_group("configure options")
    group.add_argument("-G", "--cmake-generator", action="store",
        help="Specify the CMake generator")
    group.add_argument("-D", dest="cmake_flags",
        action="append",
        help="additional cmake flags")
    group.add_argument("--no-clean-first", dest="clean_first",
        action="store_false",
        help="do not clean CMake cache")
    group.add_argument("--debug-trycompile", dest="debug_trycompile",
        action="store_true",
        help="pass --debug-trycompile to CMake call")
    group.add_argument("--eff-c++", dest="effective_cplusplus",
        action="store_true",
        help="activate warnings from the 'Effective C++' book (gcc only)")
    group.add_argument("--werror", dest="werror",
        action="store_true",
        help="treat warnings as error")
    group.add_argument("--profiling", dest="profiling", action="store_true",
        help="profile cmake execution")
    group.add_argument("--summarize-options", dest="summarize_options",
                        action="store_true",
                        help="summarize build options at the end")
    group.add_argument("--trace-cmake", dest="trace_cmake",
                      action="store_true",
                      help="run cmake in trace mode")
    group.add_argument("--coverage", dest="coverage",
                       action="store_true",
                       help="activate coverage support (gcc only)")
    group.add_argument("--32-bits", dest="force_32_bits",
                       action="store_true", help="force 32 bits build")
    group.add_argument("--with-debug-info", action="store_true", dest="debug_info",
                        help="include debug information in binaries, even when used with --release. "
                             "Note that you can also use --build-type=RelWithDebInfo "
                             "for the same effect")
    group.add_argument("--without-debug-info", action="store_false", dest="debug_info",
                        help="remove debug information from binaries, even when used with --debug")
    group.add_argument("--release", action="store_const", const="Release",
        dest="build_type",
        help="Build in release")
    group.add_argument("--debug", action="store_const", const="Debug",
        dest="build_type",
        help="Build in debug, default")
    group.add_argument("--build-type", dest="build_type",
        help="Set CMAKE_BUILD_TYPE")
    parser.set_defaults(clean_first=True, effective_cplusplus=False,
                        werror=False, profiling=False,
                        trace_cmake=False, debug_info=None,
                        build_type="Debug")

def convert_cmake_args_to_flags(args):
    """ Convert 'helper' options into cmake flags

    """
    if not args.cmake_flags:
        args.cmake_flags = list()
    if args.effective_cplusplus:
        args.cmake_flags.append("QI_EFFECTIVE_CPP=ON")
    if args.werror:
        args.cmake_flags.append("QI_WERROR=ON")
    if args.coverage:
        args.cmake_flags.append("QI_WITH_COVERAGE=ON")
    # args.debug_info has 3 values: None (not set at all), True, False
    if args.debug_info is True:
        args.cmake_flags.append("QI_WITH_DEBUG_INFO=ON")
    if args.debug_info is False:
        args.cmake_flags.append("QI_WITH_DEBUG_INFO=OFF")
    if args.force_32_bits:
        args.cmake_flags.append("QI_FORCE_32_BITS=ON")

def project_parser(parser, positional=True):
    """Parser settings for every action using several build projects."""
    group = qisys.parsers.project_parser(parser, positional=positional)
    # --use-deps is only useful when it would make more sense to
    # NOT solve the deps by default (for instance for `qibuild test`)
    group.add_argument("--use-deps", action="store_true", dest="use_deps",
                       help="Force deps resolution")
    group.add_argument("--build-deps-only", action="store_const",
                       const=["build"], dest="dep_types",
                       help="Work on specified projects by ignoring "
                             "the runtime deps.")
    parser.set_defaults(dep_types="default")

def get_build_worktree(args, verbose=True):
    """ Get a build worktree to use from a argparse.Namespace
    object

    """
    worktree = qisys.parsers.get_worktree(args)
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    if verbose:
        ui.info(ui.green, "Current build worktree:", ui.reset, ui.bold,
                build_worktree.root)
    build_config = get_build_config(build_worktree, args)
    build_worktree.build_config = build_config

    if verbose:
        if build_config.local_cmake:
            ui.info(ui.green, "Using additional cmake file", ui.blue,
                    build_config.local_cmake)
        if build_config.toolchain:
            ui.info(ui.green, "Using toolchain:", ui.blue,
                    build_config.toolchain.name)
        for profile in build_config.profiles:
            ui.info(ui.green, "Using profile:", ui.blue, profile)

    return build_worktree

def get_build_projects(build_worktree, args, solve_deps=True, default_all=False):
    """ Get a list of build projects to use from an argparse.Namespace
    object. Useful when you do not need a CMakeBuilder.
    You can choose whether or not to solve the dependencies

    """
    parser = BuildProjectParser(build_worktree)
    projects = parser.parse_args(args, default_all=default_all)
    if not solve_deps or args.single:
        return projects
    dep_types = get_dep_types(args)
    deps_solver = qibuild.deps.DepsSolver(build_worktree)
    return deps_solver.get_dep_projects(projects, dep_types)

def get_one_build_project(build_worktree, args):
    """ Get one build project from the command line.
    (zero or one project name may be specified)

    """
    parser = BuildProjectParser(build_worktree)
    projects = parser.parse_args(args)
    if not len(projects) == 1:
        raise Exception("This action can only work on one project")
    return projects[0]

def get_dep_types(args, default=None):
    """ Get a list of dep types from the command line """
    if not default:
        default = ["build", "runtime", "test"]
    if args.single:
        return list()
    if not hasattr(args, "dep_types") or args.dep_types == "default":
        return default
    return args.dep_types

def get_cmake_builder(args, default_dep_types=None):
    """ Get a :py:class:`.CMakeBuilder` object from the command line

    """
    build_worktree = get_build_worktree(args)
    # dep solving will be made later by the CMakeBuilder
    build_projects = get_build_projects(build_worktree, args, solve_deps=False)
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, build_projects)
    cmake_builder.dep_types = get_dep_types(args, default=default_dep_types)
    return cmake_builder

def get_host_tools_builder(args):
    """ Get a :py:class:`.CMakeBuilder  object from the command line
    suitable to build host dependencies

    """
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)
    host_config = qibuild_cfg.get_host_config()
    if args.config and args.config != host_config:
        raise Exception("""\
Trying to get a host tools builder with the following
build config: {config}, but the given config is not
marked as a host config\
""".format(config=args.config))
    build_worktree = get_build_worktree(args)
    if host_config:
        build_worktree.set_active_config(host_config)
    host_projects = get_host_projects(build_worktree, args)
    cmake_builder = qibuild.cmake_builder.CMakeBuilder(build_worktree, host_projects)
    return cmake_builder

def get_host_projects(build_worktree, args):
    projects = list()
    if args.all:
        projects = build_worktree.build_projects
    else:
        if args.projects:
            for project_name in args.projects:
                project = build_worktree.get_build_project(project_name, raises=True)
                projects.append(project)
        else:
            projects = [get_one_build_project(build_worktree, args)]
    deps_solver = qibuild.deps.DepsSolver(build_worktree)
    return deps_solver.get_host_projects(projects)

def get_build_config(build_worktree, args):
    """ Get a CMakeBuildConfig object from an argparse.Namespace object

    """
    build_config = build_worktree.build_config
    if hasattr(args, "config"):
        if args.config:
            build_config.set_active_config(args.config)
    if hasattr(args, "build_type"):
        build_config.build_type = args.build_type
    if hasattr(args, "cmake_generator"):
        build_config.cmake_generator = args.cmake_generator
    if hasattr(args, "verbose_make"):
        build_config.verbose_make= args.verbose_make
    if hasattr(args, "cmake_flags") and args.cmake_flags:
        # should be a list a strings looking like key=value
        user_flags = list()
        for flag_string in args.cmake_flags:
            if "=" not in flag_string:
                raise Exception("Expecting a flag looking like -Dkey=value")
            (key, value) = flag_string.split("=", 1)
            user_flags.append((key, value))
        build_config.user_flags = user_flags
    if hasattr(args, "num_jobs"):
        build_config.num_jobs = args.num_jobs
    if hasattr(args, "build_prefix"):
        if args.build_prefix:
            build_config.build_prefix = args.build_prefix
    return build_config

##
# Implementation details


class BuildProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a BuildWorkTree """

    def __init__(self, build_worktree):
        self.build_worktree = build_worktree

    def all_projects(self, args):
        return self.build_worktree.build_projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        mathes the current directory

        """
        # step 1: find the closest buildable project
        parser = qisys.parsers.WorkTreeProjectParser(self.build_worktree.worktree)
        worktree_projects = parser.parse_no_project(args)
        if not worktree_projects:
            raise CouldNotGuessProjectName()

        # WorkTreeProjectParser returns None or a list of one element
        worktree_proj = worktree_projects[0]
        build_proj = qisys.parsers.find_parent_project(self.build_worktree.build_projects,
                                                       worktree_proj.path)
        if not build_proj:
            # step 2: if we can't find, still look for a qiproject.xml not
            # registered yet and add it to the worktree:
            build_proj = qibuild.worktree.new_build_project(self.build_worktree,
                                                            worktree_proj)
        if not build_proj:
            # give up:
            raise CouldNotGuessProjectName()

        return self.parse_one_project(args, build_proj.name)

    def parse_one_project(self, args, project_arg):
        """ Accept both an absolute path matching a worktree project,
        or a project src

        """
        project = self.build_worktree.get_build_project(project_arg, raises=True)
        return [project]

class CouldNotGuessProjectName(Exception):
    def __str__(self):
        return """
Could not guess qibuild project name from current working directory
Please go inside a project, or specify the project name
on the command line
"""
