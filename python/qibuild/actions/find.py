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

""" Find a package

"""

import os
import sys
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("--cflags",
        help="Outputs required compiler flags")
    parser.add_argument("--libs",
        help="Ouputs required linnker flags")
    parser.add_argument("package")
    parser.add_argument("project_name", nargs="?", metavar="project",
        help="The name of a project")
    parser.set_defaults(quiet=True)


def do(args):
    """Main entry point """
    toc = qibuild.toc.toc_open(args.work_tree, args)
    package = args.package
    project_name = args.project_name
    if not project_name:
        project_name = qibuild.toc.project_from_cwd()


    project = toc.get_project(project_name)
    cmake_cache = os.path.join(project.build_directory, "CMakeCache.txt")
    if not os.path.exists(cmake_cache):
        print "Could not find CMakeCache for project %s" % project_name
        print "Try using `qibuild configure` first"
        sys.exit(2)
    cache = qibuild.read_cmake_cache(cmake_cache)
    u_package = package.upper()

    u_package_dir = cache.get(u_package + "_DIR")
    if not u_package_dir or u_package_dir.endswith("-NOTFOUND"):
        print "No such package: ", package
        cmake_find_root_path = cache.get("CMAKE_FIND_ROOT_PATH")
        if cmake_find_root_path:
            print "Looked in this directories: "
            paths = cmake_find_root_path.split(";")
            paths.sort()
            for path in paths:
                print "  ", path
        keys = cache.keys()
        keys.sort()
        keys = [k for k in keys if k.startswith(u_package)]
        if keys:
            print "Here are the list of relative CMake variables:"
            for key in keys:
                print key, cache[key]
        sys.exit(2)

    print "Package", package
    libs = cache.get(u_package + "_LIBRARIES")
    if libs:
        print " libraries:"
        libs = libs.split(";")
        # FIXME: fix this on windows
        libs = [x for x in libs if x != "general"]
        for lib in libs:
            print " " * 4 + lib
    inc_dirs = cache.get(u_package + "_INCLUDE_DIRS")
    if inc_dirs:
        print " include dirs:"
        inc_dirs = inc_dirs.split(";")
        for inc_dir in inc_dirs:
            print " " * 4 + inc_dir





