
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010, 2011 Aldebaran Robotics
##

import os
import platform
import logging
import qitools.configstore
import qitools.qiworktree

from   qibuild.sort        import topological_sort
from   qibuild.project     import Project
import qitools.sh
from   qitools.qiworktree import QiWorkTree
from   qibuild.toolchain  import Toolchain

LOGGER = logging.getLogger("qibuild.toc")


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
        project_dir = qitools.qiworktree.search_manifest_directory(os.getcwd())
        if project_dir:
            LOGGER.debug("Found %s from current working directory", os.path.split(project_dir)[-1])
            project_names = [ os.path.split(project_dir)[-1] ]

    if args.all:
        LOGGER.debug("Using all projects")
        project_names = toc.buildable_projects.keys()

    if not project_names:
        raise Exception("No project specified")

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



class Toc(QiWorkTree):
    def __init__(self, work_tree, build_type, toolchain_name, build_config, cmake_flags):
        """
            work_tree      = a toc worktree
            build_type     = a build type, could be debug or release
            toolchain_name = by default the system toolchain is used
            cmake_flags    = optional additional cmake flags
            build_config   = optional a build configuration
        """
        QiWorkTree.__init__(self, work_tree)
        self.build_type        = build_type
        self.toolchain         = Toolchain(toolchain_name)
        self.build_config      = build_config
        self.cmake_flags       = cmake_flags
        self.build_folder_name = None
        self.projects          = dict()

        self.toolchain.update(self)
        self._set_build_folder_name()

        if not self.build_config:
            self.build_config = self.configstore.get("general", "build", "config", default=None)

        for pname, ppath in self.buildable_projects.iteritems():
            project = Project(ppath)
            project.update_build_config(self, self.build_folder_name)
            project.update_depends(self)
            self.projects[pname] = project

        self.set_build_env()

    def resolve_deps(self, projects, runtime=False):
        """Given a list of projects, resolve the dependencies, and return
        them in topological sorted order.

        proj_list is a list of Project objects,
        the result is a list of Project objects.
        """
        LOGGER.debug("Resolving deps for %s", str(projects))
        to_sort = dict()
        for proj in self.buildable_projects.keys():
            if runtime:
                to_sort[proj] = self.projects[proj].rdepends
            else:
                to_sort[proj] = self.projects[proj].depends
        # Note: topological_sort only use lists of strings:
        res_names = topological_sort(to_sort, projects)
        LOGGER.debug("Result(runtime=%d): %s", runtime, str(res_names))
        return res_names

    def using_visual_studio(self):
        """Checks if user wants to use visual studio:
        In this case, he must have set cmake_generator to something like
        "Visual Studio 9 2008"

        """
        generator = self.configstore.get("general", "build", "cmake_generator")
        if not generator:
            return False
        return "Visual Studio" in generator

    def get_vc_version(self):
        """Return 2008, 20005 or 2010 depending of
        cmake_generator setting

        """
        generator = self.configstore.get("general", "build", "cmake_generator")
        return generator.split()[-1]



    def _set_build_folder_name(self):
        """Get a reasonable build folder.
        The point is to be sure we don't have two incompatible build configurations
        using the same build dir.

        Return a string looking like
        build-linux-release
        build-cross-debug ...
        """
        res = ["build"]
        if self.toolchain.name != "system":
            res.append(self.toolchain.name)
        else:
            res.append("sys-%s-%s" % (platform.system().lower(), platform.machine().lower()))
        if not self.using_visual_studio() and self.build_type != "debug":
            # When using cmake + visual studio, sharing the same build dir with
            # several build config is mandatory.
            # Otherwise, it's not a good idea, so we always specify it
            # when it's not "debug"
            res.append(self.build_type)

        if self.build_config:
            res.append(self.build_config)

        if self.using_visual_studio():
            res.append("vs%s" % self.get_vc_version())

        self.build_folder_name = "-".join(res)

    def get_sdk_dirs(self, project):
        """ return a list of sdk, needed to build a project """
        dirs = list()

        projects = self.resolve_deps(project)
        projects.remove(project)

        #TODO: handle toolchain, at the moment this is not correct.
        #we can add the sdk for boost (from source), even if boost is provided
        #by a toolchain
        for project in projects:
            if project in self.buildable_projects.keys():
                dirs.append(self.projects[project].get_sdk_dir())
            else:
                LOGGER.warning("dependency not found: %s", project)
        return dirs

    def split_sources_and_binaries(self, projects):
        """ split a list of projects between buildable and binaries
            return (sources, provided, notfound)
        """
        tocuild  = []
        notfound = []
        provided = []
        for project in projects:
            if project in self.toolchain.projects:
                provided.append(project)
            elif project in self.buildable_projects.keys():
                tocuild.append(project)
            else:
                notfound.append(project)
        log  = "Split between sources and binaries for : %s\n"
        log += "  to build  : %s\n"
        log += "  provided  : %s\n"
        log += "  not found : %s\n"
        LOGGER.debug(log, ",".join(projects), ",".join(tocuild),  ",".join(provided), ",".join(notfound))
        return (tocuild, provided, notfound)

    def set_build_env(self):
        """Update os.environ using the qibuild configuration file

        """
        env = self.configstore.get("general", "env")
        if not env:
            return
        path = env.get("path")
        if not path:
            return
        path = path.strip()
        path = path.replace("\n", "")
        env_path = os.environ["PATH"]
        if not env_path.endswith(";"):
            env_path += ";"
        env_path += path
        os.environ["PATH"] = env_path

def toc_open(work_tree, args, use_env=False):
    build_config   = args.build_config
    build_type     = args.build_type
    toolchain_name = args.toolchain_name
    try:
        cmake_flags = args.cmake_flags
    except:
        cmake_flags = list()

    if not work_tree:
        work_tree = qitools.qiworktree.guess_work_tree(use_env)
    if not work_tree:
        work_tree = qitools.qiworktree.search_manifest_directory(os.getcwd())
    if work_tree is None:
        raise Exception("Could not find toc work tree, please go to a valid work tree.")
    return Toc(work_tree,
               build_type=build_type,
               toolchain_name=toolchain_name,
               build_config=build_config,
               cmake_flags=cmake_flags)



open = toc_open
