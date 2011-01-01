##
## Author(s):
##  - Dimitri Merejkowsky <dmerejkowsy@aldebaran-robotics.com>
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2010 Aldebaran Robotics
##

"""Add a new package in a toolchain dir
"""

import os
import posixpath
import logging

import qitoolchain

LOGGER = logging.getLogger("actions.qitoolchain.add")

import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.shell.action_parser(parser)
    qitoolchain.shell.toolchain_parser(parser)
    parser.add_argument("toolchain", action="store", help="the toolchain name")

def do(args):
    """Retrieve the latest version from the server, if not already
    in cache

    Then, extract the package to the toolchains subdir
    """
    cache = qitoolchain.get_toolchain_cache(self.toc, self.sdk_arch)
    remote_subdir = posixpath.join("toolchains", self.sdk_arch)
    archive_name_regexp = self.package_name
    with FtpConnection("ananas") as ftp:
        res = ftp.download(remote_subdir, [archive_name_regexp], output_dir=cache)

    if len(res) != 1:
        LOGGER.error("Excpeting exactly one result, got: %s", res)
        return

    base_dir = get_toolchain_base(self.toc, self.sdk_arch)
    extract_tar(res[0], base_dir)

    # Update the root.cmake file at the top of the toolchain dir:
    subdirs = os.listdir(base_dir)
    subdirs = [x for x in subdirs if os.path.isdir(os.path.join(base_dir, x))]
    with open(os.path.join(base_dir, "root.cmake"), "w") as root_cmake:
        for subdir in subdirs:
            root_cmake.write("qi_include_sdk(%s)\n" % subdir)


if __name__ == "__main__" :
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])
