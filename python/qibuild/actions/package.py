## Copyright (c) 2011, Aldebaran Robotics
## All rights reserved.
##
## Redistribution and use in source and binary forms, with or without
## modification, are permitted provided that the following conditions are met:
##     * Redistributions of source code must retain the above copyright
##       notice, this list of conditions and the following disclaimer.
##     * Redistributions in binary form must reproduce the above copyright
##       notice, this list of conditions and the following disclaimer in the
##       documentation and/or other materials provided with the distribution.
##     * Neither the name of the Aldebaran Robotics nor the
##       names of its contributors may be used to endorse or promote products
##       derived from this software without specific prior written permission.
##
## THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
## ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
## WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
## DISCLAIMED. IN NO EVENT SHALL Aldebaran Robotics BE LIABLE FOR ANY
## DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
## (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
## LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
## ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
## (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
## SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""Generate a binary sdk"""

import os
import logging

import qibuild

LOGGER = logging.getLogger(__name__)


def get_package_name(project,
    version=None,
    config=None):
    """Get the package name of a project.

    Recognized args are:
      version    -> if not given, will try to use version.cmake at
                    the root of the project
      config     -> if not given, do nothing, else add this at the end
                    of the package name
    """
    res = [project.name]

    if version:
        res.append(version)
    else:
        # Try to get it from project/version.cmake:
        version = qibuild.project.version_from_directory(project.directory)
        if version:
            res.append(version)

    if config:
        res.append(config)

    return "-".join(res)



def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")
    group = parser.add_argument_group("package options")
    group.add_argument("--version", help="Version of the package. "
        "Default is read from the version.cmake file")
    group.add_argument("--runtime", action="store_true",
        help="Install runtime components only")
    parser.add_argument("--internal", dest="internal",
        action="store_true",
        help = "Include internal libs in package")
    parser.set_defaults(
        cmake_flags=["CMAKE_INSTALL_PREFIX='/'"],
        compress=True,
        include_deps=False,
        internal=False,
        continuous=False,
        runtime=False)

def do(args):
    """Main entry point"""
    toc = qibuild.toc_open(args.work_tree, args)
    config = toc.active_config
    if not args.project:
        project_name = qibuild.toc.project_from_cwd()
    else:
        project_name = args.project
    project = toc.get_project(project_name)
    package_name = get_package_name(project,
        version=args.version, config=config)
    destdir = os.path.join(toc.work_tree, "package")
    destdir = os.path.join(destdir, package_name)

    if args.internal:
        args.cmake_flags.append('QI_INSTALL_INTERNAL=ON')

    qibuild.run_action("qibuild.actions.configure", [project_name, "--no-clean-first"],
        forward_args=args)
    qibuild.run_action("qibuild.actions.make", [project_name],
        forward_args=args)
    qibuild.run_action("qibuild.actions.install", [project_name, destdir],
        forward_args=args)

    if args.compress:
        LOGGER.info("Compressing package")
        archive = qibuild.archive.zip(destdir)
        LOGGER.info("Package generated in %s", archive)
        # Now, clean the destdir.
        qibuild.sh.rm(destdir)
        return archive
    else:
        return destdir

