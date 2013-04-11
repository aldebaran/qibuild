## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Collection of parser fonctions for various actions."""


def log_parser(parser):
    """Given a parser, add the options controlling log."""
    group = parser.add_argument_group("logging options")
    group.add_argument("-v", "--verbose", dest="verbose", action="store_true",
         help="Output debug messages")
    group.add_argument("--quiet", "-q", dest="quiet", action="store_true",
        help="Only output error messages")
    group.add_argument("--no-color", dest="color", action="store_false",
        help="Do not use color")
    group.add_argument("--time-stamp", dest="timestamp", action="store_true",
        help="Add timestamps before each log message")
    group.add_argument("--color", dest = "color", action = "store_false",
                       help = "Colorize output. This is the default")

    parser.set_defaults(verbose=False, quiet=False, color=True)

def default_parser(parser):
    """Parser settings for every action."""
    # Every action should have access to a proper log
    log_parser(parser)
    # Every action can use  --pdb and --backtrace
    group = parser.add_argument_group("debug options")
    group.add_argument("--backtrace", action="store_true", help="Display backtrace on error")
    group.add_argument("--pdb", action="store_true", help="Use pdb on error")
    group.add_argument("--quiet-commands", action="store_true", dest="quiet_commands",
        help="Do not print command outputs")

def worktree_parser(parser):
    """Parser settings for every action using a work tree."""
    default_parser(parser)
    parser.add_argument("-w", "--worktree", "--work-tree", dest="worktree",
        help="Use a specific work tree path.")

def project_parser(parser, positional=True):
    """Parser settings for every action using projects."""
    group = parser.add_argument_group("projects specifications options")
    group.add_argument("-a", "--all", action="store_true",
        help="Work on all projects")
    group.add_argument("-s", "--single", action="store_true",
        help="Work on specified projects without taking dependencies into account.")
    if positional:
        parser.add_argument("projects", nargs="*", metavar="PROJECT", help="Project name(s)")
    else:
        group.add_argument("-p", "--project", dest="projects", action="append",
                help="Project name(s)")
    parser.set_defaults(single=False, projects = list())
    return group

