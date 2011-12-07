## Copyright (C) 2011 Aldebaran Robotics

""" Find a package

"""

import os
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
    parser.set_defaults(quiet=True)


def do(args):
    """Main entry point """
    package = args.package
    # The algorithm is quite simple:
    # * create a temporary project, containing find_package(project)
    # * configures it with CMake
    # * parse the cache
    previous_toc = qibuild.toc.toc_open(args.work_tree, args)
    project_names = [p.name for p in previous_toc.projects]
    cache = dict()
    with qibuild.sh.TempDir() as tmp:
        dummy = os.path.join(tmp, "dummy")
        qibuild_cmake_src  = os.path.join(qibuild.CMAKE_QIBUILD_DIR, "templates", "qibuild.cmake")
        qibuild_cmake_dest = os.path.join(dummy, "qibuild.cmake")
        qibuild.sh.install(qibuild_cmake_src, qibuild_cmake_dest, quiet=True)
        cmake = os.path.join(dummy, "CMakeLists.txt")
        main = os.path.join(dummy, "main.cpp")
        with open(main, "w") as fp:
            fp.write("")
        template = """ # Dummy project
cmake_minimum_required(VERSION 2.8)
project(dummy)
include(qibuild.cmake)
qi_create_bin(dummy main.cpp)
qi_use_lib(dummy {package})
"""
        with open(cmake, "w") as fp:
            fp.write(template.format(package=package))
        manifest = os.path.join(dummy, "qibuild.manifest")
        template = """[project dummy]
depends = {depends}
"""
        with open(manifest, "w") as fp:
            fp.write(template.format(depends=" ".join(project_names)))

        work_tree = args.work_tree
        if not work_tree:
            work_tree = qibuild.worktree.guess_work_tree()
        toc = qibuild.toc.Toc(work_tree,
               config=args.config,
               build_type=args.build_type,
               cmake_generator=args.cmake_generator,
               path_hints=[dummy])
        project_names = toc.buildable_projects.keys()
        with open(manifest, "w") as fp:
            fp.write(template.format(depends=" ".join(project_names)))

        qibuild.command.CONFIG["quiet"] = True
        dummy_proj = toc.get_project("dummy")
        toc.configure_project(dummy_proj, quiet=True)
        build_dir = dummy_proj.build_directory
        cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
        cache = qibuild.read_cmake_cache(cmake_cache)

    u_package = package.upper()
    keys = cache.keys()
    keys.sort()
    keys = [k for k in keys if k.startswith(u_package)]

    u_package_dir = cache.get(u_package + "_DIR")
    cmake_find_root_path = cache.get("CMAKE_FIND_ROOT_PATH")
    if not u_package_dir:
        # Should not happen
        print "Could not check if %s was found or not"
        print "Please file a bug report"
        return

    if u_package_dir.endswith("-NOTFOUND"):
        print "No such package: ", package
        if cmake_find_root_path:
            print "Looked in this directories: "
            paths = cmake_find_root_path.split(";")
            paths.sort()
            for path in paths:
                if dummy in path:
                    continue
                print "  ", path
        return

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





