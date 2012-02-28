## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Collection of parser fonctions for various actions
"""

import qibuild

def log_parser(parser):
    """ Given a parser, add the options controlling log
    """
    group = parser.add_argument_group("logging options")
    group.add_argument("-v", "--verbose", dest="verbose", action="store_true",
         help="Output debug messages")
    group.add_argument("--quiet", "-q", dest="quiet", action="store_true",
        help="Only output error messages")
    group.add_argument("--no-color", dest="color", action="store_false",
        help="Do not use color")
    group.add_argument("--color", dest = "color", action = "store_false",
                       help = "Colorize output. This is the default")

    parser.set_defaults(verbose=False, quiet=False, color=True)

def default_parser(parser):
    """ Parser settings for every action
    """
    # Every action should have access to a proper log
    log_parser(parser)
    # Every action can use  --pdb and --backtrace
    group = parser.add_argument_group("debug options")
    group.add_argument("--backtrace", action="store_true", help="Display backtrace on error")
    group.add_argument("--pdb", action="store_true", help="Use pdb on error")
    group.add_argument("--quiet-commands", action="store_true", dest="quiet_commands",
        help="Do not print command outputs")

def work_tree_parser(parser):
    """ Parser settings for every action using a work tree.
    """
    default_parser(parser)
    parser.add_argument("--work-tree", help="Use a specific work tree path.")

def toc_parser(parser):
    """ Parser settings for every action using a toc dir
    """
    work_tree_parser(parser)
    parser.add_argument('-c', '--config',
        help='The configuration to use. '
             'If a toolchain exists with the same name '
             'exists it will be used. '
             'The settings from [config "<name>"] sections will '
             'also be used')

def build_parser(parser):
    """ Parser settings for every action doing builds
    """
    group = parser.add_argument_group("build configuration arguments")
    group.add_argument("--release", action="store_const", const="release",
        dest="build_type",
        help="Build in release (set CMAKE_BUILD_TYPE=RELEASE)")
    group.add_argument("--debug", action="store_const", const="debug",
        dest="build_type",
        help="Build in debug (set CMAKE_BUILD_TYPE=DEBUG)")
    group.add_argument("--build-type", action="store",
        dest="build_type",
        help="CMAKE_BUILD_TYPE usually DEBUG or RELEASE")
    group.add_argument("--cmake-generator", action="store",
        help="Specify the CMake generator")
    group.add_argument("-j", dest="num_jobs", type=int,
        help="Number of jobs to use")
    parser.set_defaults(debug=True)
    parser.set_defaults(num_jobs=1)
    parser.set_defaults(build_type="debug")

def project_parser(parser):
    """ Parser settings for every action using several toc projects
    """
    parser.add_argument("-a", "--all", action="store_true",
        help="Work on all projects")
    parser.add_argument("-s", "--single", action="store_true",
        help="Work on specified projects without taking dependencies into account.")
    parser.add_argument("projects", nargs="*", metavar="PROJECT", help="Project name(s)")
    parser.set_defaults(single=False, projects = list())
