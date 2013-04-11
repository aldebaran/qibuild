## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for various actions
"""

import qisys.parsers

log_parser = qisys.parsers.log_parser
default_parser  = qisys.parsers.default_parser
worktree_parser = qisys.parsers.worktree_parser



def toc_parser(parser):
    """Parser settings for every action using a toc dir."""
    worktree_parser(parser)
    parser.add_argument("-c", "--config",
        help="The configuration to use. "
             "It should match the name of a toolchain. "
             "The settings from <worktree>/.qi/<config>.cmake will "
             "also be used")
    parser.add_argument("-p", "--profile", dest="profiles", action="append",
        help="A profile to use. "
             "It should match a declaration in .qi/worktree.xml")

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

def build_parser(parser):
    """Parser settings for every action doing builds."""
    group = parser.add_argument_group("build configuration options")
    build_type_parser(parser, group=group)
    group.add_argument("-G", "--cmake-generator", action="store",
        help="Specify the CMake generator")
    group.add_argument("-j", dest="num_jobs", type=int,
        help="Number of jobs to use")
    parser.set_defaults(num_jobs=1)

def project_parser(parser):
    """Parser settings for every action using several toc projects."""
    group = qisys.parsers.project_parser(parser)
    group.add_argument("--build-deps", action="store_true",
        help="Work on specified projects by ignoring the runtime deps. "
             "Useful when you have lots of runtime plugins you don't want to compile "
             "for instance")
    group.add_argument("--runtime", action="store_true",
        help="Work on specified projects by using only the runtime deps. "
             "Mostly used by qibuild install --runtime")
    parser.set_defaults(build_deps=False)
