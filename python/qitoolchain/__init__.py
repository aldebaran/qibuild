##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsky@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""  This module contains a few useful functions
"""

import posixpath
import os
import logging
import qibuild.sh

LOGGER = logging.getLogger("qitoolchain")

def get_config_path():
    home = os.getenv('USERPROFILE') or os.getenv('HOME')
    return os.path.join(home, ".config", "qi")

def get_cache(toolchain_name):
    """Return the path to the toolchain cache:
       where the zip will be kept, and so on.
    """
    return os.path.join(get_config_path(), "toolchain", "cache", toolchain_name)

def get_rootfs(toolchain_name):
    """Return the path to a toolchain directory
    """
    return os.path.join(get_config_path(), "toolchain", "rootfs", toolchain_name)


def create(toolchain_name):
    """ Check that initialization of the toolchain
        directory went well
    """
    rootfs = get_rootfs(toolchain_name)
    if os.path.exists(rootfs):
        raise Exception("Toolchain '%s' already exists." % toolchain_name)
    qibuild.sh.mkdir(rootfs, recursive=True)
    cache = get_cache(toolchain_name)
    if not os.path.exists(cache):
        qibuild.sh.mkdir(cache,  recursive=True)
    LOGGER.info("Toolchain initialized in: %s", rootfs)



def get(toolchain, package):
    """Retrieve the latest version from the server, if not already
    in cache

    Then, extract the package to the toolchains subdir
    """
    cache = get_cache(toolchain.name)
    remote_subdir = posixpath.join("toolchains", toolchain)
    archive_name_regexp = package
    with FtpConnection("ananas") as ftp:
        res = ftp.download(remote_subdir, [archive_name_regexp], output_dir=cache)

    if len(res) != 1:
        LOGGER.error("Excpeting exactly one result, got: %s", res)
        return

    base_dir = get_rootfs(toolchain)
    extract_tar(res[0], base_dir)

    # Update the root.cmake file at the top of the toolchain dir:
    subdirs = os.listdir(base_dir)
    subdirs = [x for x in subdirs if os.path.isdir(os.path.join(base_dir, x))]
    with open(os.path.join(base_dir, "root.cmake"), "w") as root_cmake:
        for subdir in subdirs:
            root_cmake.write("qi_include_sdk(%s)\n" % subdir)
