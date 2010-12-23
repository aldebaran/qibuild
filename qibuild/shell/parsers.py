"""Collection of parser fonctions for various actions

"""

def log_parser(parser):
    """Given a parser, add the options controling log

    """
    group = parser.add_argument_group("logging arguments")
    group.add_argument("-v", "--verbose", dest="verbose", action="store_true",
        help="output debug messages")
    group.add_argument("--quiet", "-q", dest="quiet", action="store_true",
        help="output only error messages")
    group.add_argument("--no-color", dest="color", action="store_false",
        help="do not use color")
    parser.set_defaults(verbose=False, quiet=False, color=True)


def action_parser(parser):
    """Parser settings for every action"""
    # Every action should have access to a proper log
    log_parser(parser)
    # Every action can use  --pdb and --backtrace
    group = parser.add_argument_group("debug arguments")
    group.add_argument("--backtrace", action="store_true",
        help="display backtrace on error")
    group.add_argument("--pdb", action="store_true",
        help="use pdb on error")

def toc_parser(parser):
    """Parser settings for every action using a toc dir

    """
    action_parser(parser)
    parser.add_argument("--toc-work-tree", help="force toc work tree")

def build_parser(parser):
    """Parser settings for every action doing
    builds

    """
    group = parser.add_argument_group("build configuration arguments")
    group.add_argument("--cross", action="store_true", help="for cross-compiling")
    group.add_argument("--ctc--path", dest="ctc_path", help="path for the cross toolchain to use")
    group.add_argument("--release", action="store_true", dest="release", help="build in release")
    group.add_argument("--debug", action="store_false",  dest="release", help="build in debug")
    group.add_argument("--config", "-c", dest="build_config",
        help="build configuration to use. Should match a setting in ~/.toc/base.cfg")
    group.add_argument("--cmake-generator",
        help="cmake generator")
    group.add_argument("-j", dest="num_jobs", type=int, help="number of jobs to use")
    parser.set_defaults(cmake_generator = "Unix Makefiles")
    parser.set_defaults(cross=False, debug=True)
    parser.set_defaults(num_jobs=1)

def project_parser(parser):
    """Parser settings for every action using several toc projects

    """
    parser.add_argument("-s", "--single", action="store_true",
        help="do not resolve any dependency")
    parser.add_argument("--only-deps", action="store_true",
        help="only work on the dependencies")
    parser.add_argument("--use-deps", action="store_true",
        help="use dependencies")
    parser.add_argument("projects", nargs="?", metavar="PROJECT",
        action="append", help="project name (s)")
    parser.set_defaults(single=False, only_deps=False, use_deps=True)

