## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Collection of parser fonctions for various actions."""

import abc
import argparse
import multiprocessing
import os

import qisys.sh
import qisys.worktree

class SetHome(argparse.Action):
    """argparse action that calls qisys.sh.set_home on the argument value"""

    def __init__(self, *args, **kwargs):
        super(SetHome, self).__init__(*args, **kwargs)

    def __call__(self, parser, namespace, values, option_string):
        qisys.sh.set_home(values)

def cpu_count():
    try:
        default = multiprocessing.cpu_count()
    except NotImplementedError:
        default = 1

def parallel_parser(parser, default=cpu_count()):
    """Given a parser, add the -j option.

    Sets variable 'num_jobs'.
    Use the number of processors as the default
    """

    parser.add_argument("-j", "--njobs",
        dest="num_jobs", type=int, default=default, metavar='N',
        help="Specify the number of jobs to run simultaneously "
             "(default: %(default)s)")

def log_parser(parser):
    """Given a parser, add the options controlling log."""
    group = parser.add_argument_group("logging options")
    group.add_argument("-v", "--verbose", dest="verbose", action="store_true",
         help="Output debug messages")
    group.add_argument("--quiet", "-q", dest="quiet", action="store_true",
        help="Only output error messages")
    group.add_argument("--time-stamp", dest="timestamp", action="store_true",
        help="Add timestamps before each log message")
    group.add_argument("--color", choices=["always", "never", "auto"],
        help="Colorize output, defaults to 'auto'")
    group.add_argument("--title", choices=["always", "never", "auto"],
        help="Update terminal title, defaults to 'auto'")

    parser.set_defaults(verbose=False, quiet=False, color="auto", title="auto")

def default_parser(parser):
    """Parser settings for every action."""
    # Every action should have access to a proper log
    log_parser(parser)
    parser.add_argument("--home", action=SetHome,
        help="Store global data in this directory instead of HOME")
    # Every action can use  --pdb and --backtrace
    group = parser.add_argument_group("debug options")
    group.add_argument("--backtrace", action="store_true", help="Display backtrace on error")
    group.add_argument("--pdb", action="store_true", help="Use pdb on error")

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
    group.add_argument("-g", "--group", dest="groups", action="append",
                       help="Specify a group of projects.")

    if positional:
        group.add_argument("projects", nargs="*", metavar="PROJECT",
                            help="Project name(s)")
    else:
        group.add_argument("-p", "--project", dest="projects", action="append",
                help="Project name(s)")
    parser.set_defaults(single=False, projects = list())
    return group

def build_parser(parser, group=None, include_worktree_parser=True):
    """Parser settings for builders."""
    if include_worktree_parser:
        worktree_parser(parser)
    if not group:
        group = parser.add_argument_group("build type options")
    group.add_argument("-c", "--config",
        help="The configuration to use. ")
    group.add_argument("--build-prefix", dest="build_prefix",
                    help="Prefix for all the build directories")

def deploy_parser(parser):
    group = parser.add_argument_group("deploy options")
    group.add_argument("--url", dest="urls", action="append",
                       help="deploy to each given url.", required=True)

def get_deploy_urls(args):
    return [qisys.remote.URL(x) for x in args.urls]

def get_worktree(args=None, raises=True):
    """ Get a worktree right after argument parsing.

    If --worktree was not given, try to guess it from
    the current working directory

    """
    wt_root = None
    if args:
        wt_root = args.worktree
    if not wt_root:
        wt_root = qisys.worktree.guess_worktree(raises=raises)
    if wt_root:
        return qisys.worktree.WorkTree(wt_root)
    else:
        return None

def get_projects(worktree, args):
    """ Get a list of worktree projects from the command line """
    parser = WorkTreeProjectParser(worktree)
    return parser.parse_args(args)

def get_one_project(worktree, args):
    parser = WorkTreeProjectParser(worktree)
    projects = parser.parse_args(args)
    if projects is None:
        raise Exception("No project found")
    if not len(projects) == 1:
        raise Exception("This action can only work with one project")
    return projects[0]

##
# Implementation details

class AbstractProjectParser(object):
    """ Helper for get_projects() methods """
    __metaclass__ = abc.ABCMeta
    def __init__(self):
        pass

    @abc.abstractmethod
    def parse_no_project(self, args):
        pass

    @abc.abstractmethod
    def parse_one_project(self, args, project_arg):
        pass

    @abc.abstractmethod
    def all_projects(self, args):
        pass

    def parse_args(self, args, default_all=False):
        """ Parse arguments. args may be a
        argparse.Namespace() object, or a dict

        """
        if isinstance(args, dict):
            args = argparse.Namespace(**args)
        if not hasattr(args, "all"):
            args.all = False
        if not hasattr(args, "single"):
            args.single = False
        if args.all and args.single:
            raise Exception("Cannot use --single with --all")
        # pylint: disable-msg=E1103
        if args.all:
            return self.all_projects(args)
        project_args = args.projects
        # pylint: disable-msg=E1103
        if not args.projects:
            if default_all and not args.single:
                return self.all_projects(args)
            else:
                return self.parse_no_project(args)
        res = list()
        for project_arg in project_args:
            # parsing one arg can result in several projets
            # (for instance if there are deps)
            res.extend(self.parse_one_project(args, project_arg))
        return res

class WorkTreeProjectParser(AbstractProjectParser):
    """ Implements AbstractProjectParser for a basic WorkTree """

    def __init__(self, worktree):
        self.worktree = worktree

    def all_projects(self, args):
        return self.worktree.projects

    def parse_no_project(self, args):
        """ Try to find the closest worktree project that
        mathes the current directory

        """
        res = find_or_add(self.worktree)
        if res:
            return [res]

    def parse_one_project(self, args, project_arg):
        """ Accept both an absolute path matching a worktree project,
        or a project src

        """
        # assume absolute path
        as_path = qisys.sh.to_native_path(project_arg)
        if os.path.exists(as_path):
            parent_project = find_parent_project(self.worktree.projects, as_path)
            if parent_project:
                return [parent_project]

        # Now assume it is a project src
        project = self.worktree.get_project(project_arg, raises=True)
        return [project]

def find_parent_project(projects, path):
    """ Find the parent project of a given path """
    projs = projects[:]
    projs.reverse()
    for project in projs:
        if qisys.sh.is_path_inside(path, project.path):
            return project

def find_or_add(worktree, cwd=None):
    """ If we find a qiproject.xml in a path not
    registered yet by looking in the parent
    directories, we just add it to the list

    """
    if cwd is None:
        cwd = os.getcwd()
    head = cwd
    tail = None
    while True:
        candidate = os.path.join(head, "qiproject.xml")
        project = worktree.get_project(head)
        if project:
            return project
        if os.path.exists(candidate):
            return worktree.add_project(head)
        (head, tail) = os.path.split(head)
        if not tail:
            break
