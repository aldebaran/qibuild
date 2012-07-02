## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Display dependencies of projects

"""

import qibuild
import qibuild.ui
from qibuild.dependencies_solver import DependenciesSolver

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("depends arguments")
    parser.add_argument("--reverse", "-r", action="store_true", help="display reverse dependencies")
    parser.add_argument("--deep", action="store_true", help="display all dependencies using a depth traversal")

def get_reverse_deps(toc, project_name):
    bproject_names = []
    rproject_names = []
    for p in toc.projects:
        dep_solver = DependenciesSolver(projects=toc.projects, packages=toc.packages, active_projects=toc.active_projects)
        (bp, _, _) = dep_solver.solve([p.name], runtime=False)
        (rp, _, _) = dep_solver.solve([p.name], runtime=True)
        if project_name in bp:
            bproject_names.append(p.name)
        if project_name in rp:
            rproject_names.append(p.name)
    return (bproject_names, rproject_names, set(), set())

def get_deps(toc, project_name):
    dep_solver = DependenciesSolver(projects=toc.projects, packages=toc.packages, active_projects=toc.active_projects)
    (bproject_names, bpackage_names, _) = dep_solver.solve([project_name], runtime=False)
    (rproject_names, rpackage_names, _) = dep_solver.solve([project_name], runtime=True)
    return (bproject_names, rproject_names, bpackage_names, rpackage_names)

def do(args):
    """Main entry point"""
    logger   = qibuild.log.get_logger(__name__)
    toc      = qibuild.toc_open(args.worktree, args)

    qibuild.ui.info("legend:",
                    qibuild.ui.red  , "buildtime",
                    qibuild.ui.white, "buildtime+runtime",
                    qibuild.ui.green, "runtime")
    qibuild.ui.info()

    active_projects = toc.active_projects
    if args.deep and not args.reverse:
        (active_projects, _, _) = toc.resolve_deps()
    elif args.deep and args.reverse:
        qibuild.ui.error("you can't use --deep with --reverse.")
        exit(1)
    for pname in active_projects:
        project = toc.get_project(pname)
        if args.reverse:
            qibuild.ui.info(qibuild.ui.green, "*", qibuild.ui.blue, project.name, qibuild.ui.reset, "reverse dependencies:")
        else:
            qibuild.ui.info(qibuild.ui.green, "*", qibuild.ui.blue, project.name, qibuild.ui.reset, "dependencies:")

        if args.reverse:
            (bproject_names, rproject_names,
             bpackage_names, rpackage_names) = get_reverse_deps(toc, pname)
        else:
            (bproject_names, rproject_names,
             bpackage_names, rpackage_names) = get_deps(toc, pname)

        bproject_names = set(bproject_names) - set([pname])
        rproject_names = set(rproject_names) - set([pname])

        brproject_names = set(bproject_names).intersection(set(rproject_names))
        brpackage_names = set(bpackage_names).intersection(set(rpackage_names))

        bproject_names = set(bproject_names) - set(brproject_names)
        rproject_names = set(rproject_names) - set(brproject_names)

        bpackage_names = set(bpackage_names) - set(brpackage_names)
        rpackage_names = set(rpackage_names) - set(brpackage_names)

        qibuild.ui.info("  projects:",
                        qibuild.ui.red  , " ".join(bproject_names),
                        qibuild.ui.white, " ".join(brproject_names),
                        qibuild.ui.green, " ".join(rproject_names))
        qibuild.ui.info("  packages:",
                        qibuild.ui.red  , " ".join(bpackage_names),
                        qibuild.ui.white, " ".join(brpackage_names),
                        qibuild.ui.green, " ".join(rpackage_names))
