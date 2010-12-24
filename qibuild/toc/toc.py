
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

import os
import sys
import logging
import qibuild.configstore
from   qibuild.sort        import topological_sort
from   qibuild.toc.project import Project

LOGGER = logging.getLogger("qibuild.toc")

def search_manifest_directory(working_directory):
    """ find the manifest associated to the working_directory, return None if not found """
    cwd     = os.path.normpath(os.path.abspath(working_directory))
    dirname = None

    #for each cwd parent folders, try to see if it match src
    while dirname or cwd:
        if (os.path.exists(os.path.join(cwd, "qibuild.manifest"))):
            return cwd
        (new_cwd, dirname) = os.path.split(cwd)
        if new_cwd == cwd:
            break
        cwd = new_cwd
    return None

def get_projects_from_args(toc, args):
    """ Return the list of project specified in args. This is usefull to extract
        a project list from command line arguments. The returned list contains

        case handled:
          - nothing specified: get the project from the cwd
          - args.single: do not resolve dependencies
          - args.only_deps: only return dependencies
          - args.use_deps: take dependencies into account
    """
    if args.projects == [ None ]:
        project_names = list()
    else:
        project_names = args.projects

    if not project_names:
        LOGGER.debug("no project specified, guessing from current working directory")
        project_dir = search_manifest_directory(os.getcwd())
        if project_dir:
            LOGGER.debug("Found %s from current working directory", os.path.split(project_dir)[-1])
            project_names = [ os.path.split(project_dir)[-1] ]

    if not project_names:
        LOGGER.debug("Using all projects")
        project_names = toc.buildable_projects.keys()

    if args.single:
        LOGGER.debug("Using a single project: %s", project_names[0])
        return project_names

    if args.only_deps:
        if len(project_names) != 1:
            raise Exception("You should have a list of exactly one project when using --single or --only-deps")
        if not args.use_deps:
            raise Exception("Conflicting options: only_deps, no_deps")
        single_project = project_names[0]

    if args.use_deps:
        project_names = toc.resolve_deps(project_names)

    if args.only_deps:
        project_names.remove(single_project)

    return project_names


def _search_buildable_projects(directory=None):
    """ search for qibuild.manifest files recursively starting from directory
        this function return a list of directory.
    """
    result = list()
    if os.path.exists(os.path.join(directory, "qibuild.manifest")):
        result.append(directory)
    for p in os.listdir(directory):
        if os.path.isdir(os.path.join(directory, p)):
            result.extend(_search_buildable_projects(os.path.join(directory, p)))
    return result

class Toc:
    """ For a toc worktree this class allow finding:
        - buildable projects
        - toolchains
    """

    def __init__(self, work_tree):
        self.work_tree          = work_tree
        self.buildable_projects = dict()
        self.configstore        = qibuild.configstore.ConfigStore()
        self._load_buildable_projects()
        self._load_configuration()


    def _load_buildable_projects(self):
        buildable_project_dirs = _search_buildable_projects(self.work_tree)
        for d in buildable_project_dirs:
            p = Project(d)
            self.buildable_projects[p.name] = p

    def _load_configuration(self):
        for name, project in self.buildable_projects.iteritems():
            qibuild.configstore.read(os.path.join(project.directory, "qibuild.manifest"), self.configstore)
        qibuild.configstore.read(os.path.join(self.work_tree, ".qibuild", "config"), self.configstore)
        LOGGER.debug("[toc] configuration:\n" + str(self.configstore))

    def get_project(self, name):
        return self.buildable_projects[name]

    def resolve_deps(self, projects):
        """Given a list of projects, resolve the dependencies, and return
        them in topological sorted order.

        proj_list is a list of Project objects,
        the result is a list of Project objects.

        """
        LOGGER.debug("Resolving deps for %s", str(projects))
        to_sort = dict()
        for proj in self.buildable_projects.keys():
            deps = self.configstore.get("project", proj, "depends").split()
            to_sort[proj] = deps
        # Note: topological_sort only use lists of strings:
        res_names = topological_sort(to_sort, projects)
        LOGGER.debug("Result: %s", str(res_names))
        return res_names

    def split_sources_and_binaries(self, projects):
        """ split a list of projects between buildable and binaries
            return (sources, binaries)

            TODO: handle toolchain
        """
        tobuild   = []
        toinstall = []
        for project in projects:
            if project in self.buildable_projects.keys():
                tobuild.append(project)
            else:
                toinstall.append(project)
        return (tobuild, toinstall)



