#!/usr/bin/env python
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

""" works with sdk
"""
import logging

LOGGER = logging.getLogger("qibuild.dependencies")

def get_sdk_dirs(project, toc):
    """ return a list of sdk, needed to build a project """
    dirs = list()

    projects = toc.resolve_deps(project)
    projects.remove(project)

    for project in projects:
        if project in toc.buildable_projects.keys():
            dirs.append(toc.get_project(project).get_sdk_dir())
        else:
            LOGGER.warning("dependency not found: %s", project)
    return dirs


def split_sources_and_binaries(projects, toc, tob=None):
    """ split a list of projects between buildable and binaries
        return (sources, binaries)

        TODO: handle toolchain
    """
    tobuild   = []
    toinstall = []
    for project in projects:
        if project in toc.buildable_projects.keys():
            tobuild.append(project)
        else:
            toinstall.append(project)
    return (tobuild, toinstall)
