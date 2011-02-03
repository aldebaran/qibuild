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
    parser.add_argument("--work-tree", help="Use a specific work tree path")

def build_parser(parser):
    """ Parser settings for every action doing builds
    """
    group = parser.add_argument_group("build configuration arguments")
    group.add_argument("--cross", action="store_true", help="Cross compile")
    group.add_argument("--ctc--path", dest="ctc_path", help="Cross toolchain path")
    group.add_argument("--release", action="store_const", const="release", dest="build_type", help="Build in release")
    group.add_argument("--debug", action="store_const", const="debug", dest="build_type", help="Build in debug")
    group.add_argument("--build-type", action="store", dest="build_type", help="CMake build type")
    group.add_argument("--build-config", "-c", dest="build_config",
                       help="Build configuration to use. Should match a setting in ~/.toc/base.cfg")
    group.add_argument("--toolchain", action="store", dest="toolchain_name", help="Use a specific toolchain")
    group.add_argument("--cmake-generator", action="store", help="Specify the CMake generator")
    group.add_argument("-j", dest="num_jobs", type=int, help="Number of jobs to use")
    parser.set_defaults(cross=False, debug=True)
    parser.set_defaults(num_jobs=1)
    parser.set_defaults(toolchain_name=None)
    parser.set_defaults(build_type="debug")

def project_parser(parser):
    """ Parser settings for every action using several toc projects
    """
    parser.add_argument("-a", "--all", action="store_true", help="Work on all projects")
    parser.add_argument("-s", "--single", action="store_true", help="Work on a single project")
    parser.add_argument("--only-deps", action="store_true", help="Only work on the dependencies")
    parser.add_argument("--use-deps",    dest="use_deps", action="store_true",
        help="Use dependencies")
    parser.add_argument("--no-use-deps", dest="use_deps", action="store_false",
        help="Do not resolve any dependencies")
    parser.add_argument("projects", nargs="*", metavar="PROJECT", help="Project name(s)")
    parser.set_defaults(single=False,
        only_deps=False,
        use_deps=True,
        projects = list())

