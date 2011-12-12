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

"""Configure a project

"""

import logging
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("cmake arguments")
    group.add_argument("--build-directory", dest="build_directory",
        action="store",
        help="override the default build directory used by cmake")
    group.add_argument("-D", dest="cmake_flags",
        action="append",
        help="additional cmake flags")
    group.add_argument("--no-clean-first", dest="clean_first",
        action="store_false",
        help="do not clean CMake cache")
    parser.set_defaults(clean_first=True)

def do(args):
    """Main entry point"""
    if args.build_directory and not args.single:
        raise Exception("You should use --single when specifying a build directory")

    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc_open(args.work_tree, args)

    (project_names, _, _) = toc.resolve_deps()

    projects = [toc.get_project(name) for name in project_names]
    if args.build_directory:
        projects[0].set_custom_build_directory(args.build_directory)

    if toc.active_config:
        logger.info("Active configuration: %s", toc.active_config)
    for project in projects:
        logger.info("Configuring %s", project.name)
        toc.configure_project(project, clean_first=args.clean_first)


