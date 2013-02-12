## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Find a package

"""

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
    parser.add_argument("project", nargs="?", metavar="project",
        help="The name of a project")
    parser.set_defaults(quiet=True)


def do(args):
    """Main entry point """
    toc = qibuild.toc.toc_open(args.worktree, args)
    package = args.package
    project = qibuild.cmdparse.project_from_args(toc, args)
    qibuild.toc.check_configure(toc, project)

    cache = qibuild.cmake.read_cmake_cache(project.cmakecache_path)
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





