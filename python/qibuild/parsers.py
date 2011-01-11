##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010, 2011 Aldebaran Robotics
##

""" Collection of parser fonctions for various actions
"""

from qitools.cmdparse import default_parser

def toc_parser(parser):
    """ Parser settings for every action using a toc dir
    """
    default_parser(parser)
    parser.add_argument("--work-tree", help="force work tree")

def build_parser(parser):
    """ Parser settings for every action doing builds
    """
    group = parser.add_argument_group("build configuration arguments")
    group.add_argument("--cross", action="store_true", help="for cross-compiling")
    group.add_argument("--ctc--path", dest="ctc_path", help="path for the cross toolchain to use")
    group.add_argument("--release", action="store_const", const="release", dest="build_type", help="build in release")
    group.add_argument("--debug", action="store_const", const="debug", dest="build_type", help="build in debug")
    group.add_argument("--build-type", action="store", dest="build_type", help="build type (CMAKE_BUILD_TYPE)")
    group.add_argument("--build-config", "-c", dest="build_config",
                       help="build configuration to use. Should match a setting in ~/.toc/base.cfg")
    group.add_argument("--toolchain", action="store", dest="toolchain_name", help="use a specific toolchain")
    group.add_argument("--cmake-generator", action="store", help="specify cmake generator")
    group.add_argument("-j", dest="num_jobs", type=int, help="number of jobs to use")
    parser.set_defaults(cross=False, debug=True)
    parser.set_defaults(num_jobs=1)
    parser.set_defaults(toolchain_name=None)
    parser.set_defaults(build_type="debug")

def project_parser(parser):
    """ Parser settings for every action using several toc projects
    """
    parser.add_argument("-a", "--all", action="store_true", help="work on all projects")
    parser.add_argument("-s", "--single", action="store_true", help="do not resolve any dependency")
    parser.add_argument("--only-deps", action="store_true", help="only work on the dependencies")
    parser.add_argument("--use-deps",    dest="use_deps", action="store_true",
        help="use dependencies")
    parser.add_argument("--no-use-deps", dest="use_deps", action="store_false",
        help="do resolve any dependency")
    parser.add_argument("projects", nargs="?", metavar="PROJECT", action="append", help="project name (s)")
    parser.set_defaults(single=False, only_deps=False, use_deps=True)

