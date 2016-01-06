## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Install a project and its dependencies """


import qisys.sh
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.cmake_build_parser(parser)
    group = parser.add_argument_group("install options")
    group.add_argument("--prefix", metavar="PREFIX",
        help="value of CMAKE_INSTALL_PREFIX, defaults to '/'")
    group.add_argument("dest_dir", metavar="DESTDIR")
    group.add_argument("--runtime", action="store_const", dest="dep_types",
                       const=["runtime"],
                       help="Only install the runtime components")
    group.add_argument("--split-debug", action="store_true",
                       help="Split debug symbols")
    group.add_argument("--with-tests", action="store_true", dest="with_tests",
                        help="Also install tests")
    group.add_argument("--no-packages", action="store_false", dest="install_tc_packages",
                        help="Do not install packages from toolchain")

    parser.set_defaults(prefix="/", split_debug=False, dep_types="default",
                        install_tc_packages=True)
    if not parser.epilog:
        parser.epilog = ""
    parser.epilog += """
Warning:
    If CMAKE_INSTALL_PREFIX was set during configure, it is necessary to repeat
    it at install using the '--prefix' option.
"""


def do(args):
    """Main entry point"""
    dest_dir = qisys.sh.to_native_path(args.dest_dir)
    cmake_builder = qibuild.parsers.get_cmake_builder(
                                    args, default_dep_types=["build", "runtime"])
    components = list()
    if args.dep_types == "default":
        if args.with_tests:
            components = ["test", "runtime"]
        else:
            components = ["devel", "runtime"]
    else:
        if "build" in args.dep_types:
            components.append("devel")
        if "runtime" in args.dep_types:
            components.append("runtime")
        if "test" in args.dep_types:
            components.append("test")

    res = cmake_builder.install(dest_dir, prefix=args.prefix,
                                split_debug=args.split_debug,
                                components=components,
                                install_tc_packages=args.install_tc_packages)
    return res
