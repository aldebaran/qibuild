## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

""" Display dependencies of projects

"""

import qibuild
import qisys.ui

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    qibuild.parsers.project_parser(parser)
    group = parser.add_argument_group("depends arguments")
    group.add_argument("--reverse", "-r", action="store_true",
                       help="display reverse dependencies")
    group.add_argument("--deep", action="store_true",
                        help="display all dependencies using a depth traversal")

def get_reverse_deps(toc, project):
    bproject_names = list()
    rproject_names = list()
    for p in toc.projects:
        (_, p_rdeps) = qibuild.cmdparse.get_deps(toc, [p], runtime=True)
        (_, p_bdeps) = qibuild.cmdparse.get_deps(toc, [p], build_deps=True)
        if project.name in [x.name for x in p_bdeps]:
            bproject_names.append(p.name)
        if project.name in [x.name for x in p_rdeps]:
            rproject_names.append(p.name)
    return (bproject_names, rproject_names, set(), set())

def get_deps(toc, project):
    (bpackages, bprojects) = qibuild.cmdparse.get_deps(toc, [project], build_deps=True)
    (rpackages, rprojects) = qibuild.cmdparse.get_deps(toc, [project], runtime=True)

    return ([x.name for x in bprojects], [x.name for x in rprojects],
            [x.name for x in bpackages], [x.name for x in rpackages])

def do(args):
    """Main entry point"""
    if args.deep and args.reverse:
        qisys.ui.error("you can't use --deep with --reverse.")
        exit(1)
    toc = qibuild.toc.toc_open(args.worktree, args)
    if args.deep:
        (_, projects) = qibuild.cmdparse.deps_from_args(toc, args)
    else:
        # small hack:
        if args.projects:
            args.project = args.projects[0]
        else:
            args.project = None
        project = qibuild.cmdparse.project_from_args(toc, args)
        projects = [project]


    qisys.ui.info("legend:",
                    qisys.ui.red  , "buildtime",
                    qisys.ui.white, "buildtime+runtime",
                    qisys.ui.green, "runtime")
    qisys.ui.info()


    for project in projects:
        if args.reverse:
            qisys.ui.info(qisys.ui.green, "*",
                            qisys.ui.blue, project.name, qisys.ui.reset,
                            "reverse dependencies:")
        else:
            qisys.ui.info(qisys.ui.green, "*",
                            qisys.ui.blue, project.name, qisys.ui.reset,
                            "dependencies:")

        if args.reverse:
            (bproject_names, rproject_names,
             bpackage_names, rpackage_names) = get_reverse_deps(toc, project)
        else:
            (bproject_names, rproject_names,
             bpackage_names, rpackage_names) = get_deps(toc, project)

        bproject_names = set(bproject_names) - set([project.name])
        rproject_names = set(rproject_names) - set([project.name])

        brproject_names = set(bproject_names).intersection(set(rproject_names))
        brpackage_names = set(bpackage_names).intersection(set(rpackage_names))

        bproject_names = set(bproject_names) - set(brproject_names)
        rproject_names = set(rproject_names) - set(brproject_names)

        bpackage_names = set(bpackage_names) - set(brpackage_names)
        rpackage_names = set(rpackage_names) - set(brpackage_names)

        qisys.ui.info("  projects:",
                        qisys.ui.red  , " ".join(bproject_names),
                        qisys.ui.white, " ".join(brproject_names),
                        qisys.ui.green, " ".join(rproject_names))
        qisys.ui.info("  packages:",
                        qisys.ui.red  , " ".join(bpackage_names),
                        qisys.ui.white, " ".join(brpackage_names),
                        qisys.ui.green, " ".join(rpackage_names))
