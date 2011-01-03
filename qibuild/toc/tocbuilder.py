##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##

import os
import sys
import platform
import logging
import qibuild.sh
import qibuild.build
from   qibuild.toc.toc       import Toc
from   qibuild.toc.toolchain import Toolchain

LOGGER = logging.getLogger("qibuild.tocbuilder")

class TocBuilder(Toc):
    def __init__(self, work_tree, build_type, toolchain_name, build_config, cmake_flags):
        """
            work_tree      = a toc worktree
            build_type     = a build type, could be debug or release
            toolchain_name = by default the system toolchain is used
            cmake_flags    = optional additional cmake flags
            build_config   = optional a build configuration
        """
        Toc.__init__(self, work_tree)
        self.build_type        = build_type
        self.toolchain         = Toolchain(toolchain_name)
        self.build_config      = build_config
        self.cmake_flags       = cmake_flags
        self.build_folder_name = None

        self.toolchain.update(self)
        self._set_build_folder_name()

        if not self.build_config:
            self.build_config = self.configstore.get("general", "build", "config", default=None)

        for project in self.buildable_projects.values():
            project.update_build_config(self, self.build_folder_name)

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
        if not sys.platform.startswith("win32") and self.build_type:
            # On windows, sharing the same build dir for debug and release is OK.
            # (and quite mandatory when using CMake + Visual studio)
            # On linux, it's not.
            res.append(self.build_type)
        if self.build_config:
            res.append(self.build_config)
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
                dirs.append(self.get_project(project).get_sdk_dir())
            else:
                LOGGER.warning("dependency not found: %s", project)
        return dirs

    def split_sources_and_binaries(self, projects):
        """ split a list of projects between buildable and binaries
            return (sources, provided, notfound)
        """
        tobuild  = []
        notfound = []
        provided = []
        for project in projects:
            if project in self.toolchain.projects:
                provided.append(project)
            elif project in self.buildable_projects.keys():
                tobuild.append(project)
            else:
                notfound.append(project)
        log  = "Split between sources and binaries for : %s\n"
        log += "  to build  : %s\n"
        log += "  provided  : %s\n"
        log += "  not found : %s\n"
        LOGGER.debug(log, ",".join(projects), ",".join(tobuild),  ",".join(provided), ",".join(notfound))
        return (tobuild, provided, notfound)
