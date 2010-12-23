"""Configure a project

"""

import os
import logging
import qibuild



def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.shell.toc_parser(parser)
    qibuild.shell.build_parser(parser)
    qibuild.shell.project_parser(parser)
    group = parser.add_argument_group("cmake arguments")
    group.add_argument("-D", dest="cmake_flags", action="append",
        help="additional cmake flags")


def do(args):
    """Main entry point"""
    logger   = logging.getLogger(__name__)
    toc      = qibuild.toc.toc_open(args.toc_work_tree, use_env=True)

    print ""
    print "buildable projects:"
    for p,v in toc.buildable_projects.iteritems():
        print " -", p, ":", toc.configstore.get("project", p, "depends")

    projects = qibuild.toc.get_projects_from_args(toc, args)

    print ""
    print "project wanted:"
    for project in projects:
        print " -", project

    tobuild   = []
    toinstall = []
    for project in projects:
        if project in toc.buildable_projects.keys():
            tobuild.append(project)
        else:
            toinstall.append(project)

    print ""
    print "project to configure:"
    for project in tobuild:
            print " -", project

    print ""
    print "project you should install in your system:"
    for project in toinstall:
            print " -", project

    #projects = qibuild.shell.get_projects(args, toc, args.projects)

    for project in tobuild:
        logger.info("Configuring [%s]", project)
        p = toc.get_project(project)
        qibuild.toc.bootstrap(p, args)
        qibuild.toc.cmake(p, args)

    # Set build configurations
    #qibuild.shell.buildaction.set_build_configs(args, toc, projects)

    #for project in projects:
    #    generate_find_deps(args, toc, project)

    # Call CMake for every dep:
    # for project in projects:
    #     logger.info("Configuring [%s]", project.name)
    #     #qibuild.shell.buildaction.run_cmake(args, project)

if __name__ == "__main__":
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])


