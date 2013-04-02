## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for various actions
"""

import os

import qisys.parsers
import qibuild.worktree



def build_type_parser(parser, group=None):
    """Parser settings for build type."""
    if not group:
        group = parser.add_argument_group("Build type options")
    group.add_argument("--release", action="store_const", const="Release",
        dest="build_type",
        help="Build in release (set CMAKE_BUILD_TYPE=Release)")
    group.add_argument("--debug", action="store_const", const="Debug",
        dest="build_type",
        help="Build in debug (set CMAKE_BUILD_TYPE=Debug)")
    group.add_argument("--build-type", action="store",
        dest="build_type",
        help="CMAKE_BUILD_TYPE usually Debug or Release")
    parser.set_defaults(build_type="Debug")

def job_parser(parser, group=None):
    """Parser settings for every action doing builds."""
    group.add_argument("-j", dest="num_jobs", type=int,
        help="Number of jobs to use")
    parser.set_defaults(num_jobs=1)

def build_parser(parser):
    """Parser settings for every action doing build.
    Calls build_type_parser and job_parser

    """
    group = parser.add_argument_group("build configuration options")
    qisys.parsers.worktree_parser(parser)
    job_parser(parser, group=group)
    build_type_parser(parser, group=group)
    group.add_argument("-G", "--cmake-generator", action="store",
        help="Specify the CMake generator")
    parser.add_argument("-c", "--config",
        help="The configuration to use. "
             "It should match the name of a toolchain. "
             "The settings from <worktree>/.qi/<config>.cmake will "
             "also be used")
    parser.add_argument("-p", "--profile", dest="profiles", action="append",
        help="A profile to use. "
             "It should match a declaration in .qi/qibuild.xml")

def project_parser(parser, positional=True):
    """Parser settings for every action using several build projects."""
    group = qisys.parsers.project_parser(parser, positional=positional, short=False)
    group.add_argument("--no-runtime", "--build-deps-only",
        action="store_true", dest="build_deps_only",
        help="Work on specified projects by ignoring the runtime deps. "
             "Useful when you have lots of runtime plugins you don't want to compile "
             "for instance")
    group.add_argument("--runtime", action="store_true",
        help="Work on specified projects by using only the runtime deps. "
             "Mostly used by qibuild install --runtime")
    parser.set_defaults(build_deps=False)

# FIXME
def toc_parser(parser):
    pass

def get_build_worktree(args):
    """ Get a build worktree to use from a argparse.Namespace
    object

    """
    worktree = qisys.parsers.get_worktree(args)
    build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    build_config = get_build_config(args)
    build_worktree.build_config = build_config
    return build_worktree

def get_build_projects(build_worktree, args):
    """ Get a list of build projects to use from an argparse.Namespace
    object

    """
    parser = BuildProjectParser(build_worktree)
    return parser.parse_args(args)



##
# Implementation details

def get_build_config(args):
    """ Get a CMakeBuildConfig object from an argparse.Namespace object

    """
    build_config = qibuild.build_config.CMakeBuildConfig()
    build_config.build_type = args.build_type
    if args.profiles:
        build_config.profiles = args.profiles
    build_config.toolchain_name = args.config
    return build_config


class BuildProjectParser(qisys.parsers.AbstractProjectParser):
    """ Implements AbstractProjectParser for a BuildWorkTree """

    def __init__(self, build_worktree):
        self.build_worktree = build_worktree

    def all_projects(self, args):
        # solve deps
        pass

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        mathes the current directory

        """
        name, path = project_name_and_path_from_cwd()
        build_proj = self.build_worktree.get_build_project(name, raises=False)
        if not build_proj:
            # auto add the build project to the worktree:
            self.build_worktree.worktree.add_project(path)
            build_proj = self.build_worktree.get_build_project(name)
        return self.parse_one_project(args, build_proj.name)

    def parse_one_project(self, args, project_arg):
        """ Accept both an absolute path matching a worktree project,
        or a project src

        """
        project = self.build_worktree.get_build_project(project_arg, raises=True)
        if args.single:
            return [project]
        deps = self.build_worktree.get_deps(project, runtime=args.runtime,
                                            build_deps_only=args.build_deps_only)
        return deps


def project_name_and_path_from_cwd():
    """ Find the parent qibuild project of a given path """
    head = os.getcwd()
    tail = None
    while True:
        candidate = os.path.join(head, "qiproject.xml")
        if os.path.exists(candidate):
            tree = qisys.qixml.read(candidate)
            # FIXME: support new syntax ?
            # FIXME: use BuildProjectParser ?
            name = tree.getroot().get("name")
            if name:
                return (name, head)
        (head, tail) = os.path.split(head)
        if not tail:
            break
    mess = """
Could not guess qibuild project name from current working directory
Please go inside a project, or specify the project name
on the command line
"""
    raise Exception(mess)
