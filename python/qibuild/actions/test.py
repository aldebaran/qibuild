## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Launch automatic tests
"""

import os
import sys

from qibuild import ui
import qibuild

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("project", nargs="?")
    parser.add_argument("-k", "--pattern", dest="pattern",
                        help="Filter tests matching this pattern")
    parser.add_argument("-n" , "--dry-run", dest="dry_run",
                        action="store_true",
                        help="Just list what tests would be run")
    parser.add_argument("--slow", action="store_true",
                        help="Also run slow tests")
    parser.add_argument("-V", action="store_true", dest="verbose_tests",
                        help="verbose tests")
    parser.set_defaults(slow=False)

def do(args):
    """Main entry point"""
    toc      = qibuild.toc_open(args.worktree, args)
    if not args.project:
        project_name = qibuild.project.project_from_cwd()
    else:
        project_name = args.project
    project = toc.get_project(project_name)

    build_dir = project.build_directory
    cmake_cache = os.path.join(build_dir, "CMakeCache.txt")
    if not os.path.exists(cmake_cache):
        qibuild.toc.advise_using_configure(toc, project)

    res = qibuild.ctest.run_tests(project, toc.build_env,
            pattern=args.pattern, slow=args.slow,
            dry_run=args.dry_run,
            verbose=args.verbose_tests)
    if not res:
        sys.exit(1)

