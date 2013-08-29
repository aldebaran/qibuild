## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Install a project and its dependencies """


import qisys.sh
import qibuild.parsers

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.project_parser(parser)
    qibuild.parsers.build_parser(parser)
    group = parser.add_argument_group("install options")
    group.add_argument("--prefix", metavar="PREFIX",
        help="value of CMAKE_INSTALL_PREFIX, defaults to '/'")
    group.add_argument("dest_dir", metavar="DESTDIR")
    group.add_argument("--runtime", action="store_const", dest="dep_types",
                       const=["runtime"],
                       help="Only install the runtime components")
    group.add_argument("--split-debug", action="store_true",
                       help="Split debug symbols")
    parser.set_defaults(prefix="/", split_debug=False, dep_types="default")
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
        components = None
    else:
        if "build" in args.dep_types:
            components.append("devel")
        if "runtime" in args.dep_types:
            components.append("runtime")
        if "test" in args.dep_types:
            components.append("test")

    cmake_builder.install(dest_dir, prefix=args.prefix,
                          split_debug=args.split_debug,
                          components=components)
