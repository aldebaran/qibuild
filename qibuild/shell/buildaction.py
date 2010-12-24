import os
import qibuild
import logging


def set_build_configs(args, toc, projects):
    """Set the build configurations of the projects and
    their deps.

    This should be called before any call to project.cmake.get_build_dir() !

    The build configurations are read from the following places, in this
    order:

    * global configuration:

         from ~/.toc/base.cfg:
            [toc general]
            build.config = lite

    * --build-config from command line:

    * project configuration:

        from path/to/project/base.cfg

        [project "foo"]
        cmake.flags = ...

    * --debug, --release, cross compilation (from command line)

    """
    logger = logging.getLogger(__name__)
    arch = qibuild.toc.buildconfig.get_arch(args.cross)
    full_list = toc.resolve_deps(projects, arch)
    for project in full_list:
        proj_build_conf = project.cmake.build_config

        proj_build_conf.update_from_toc_config(toc)
        if args.build_config:
            proj_build_conf.update_from_build_config_name(toc,
                args.build_config)
        proj_build_conf.update_from_project_config(project)
        proj_build_conf.update_from_command_line(release = args.release,
                                                 cross = args.cross,
                                                 ctc_path = args.ctc_path)
    logger.debug("[%s]\n%s", project, proj_build_conf)


def run_cmake(args, project):
    r"""Run CMake on the build dir of a project

    /!\ assumes that set_build_configs has been called

    The CMake cache and build/sdk/cmake are always cleaned.
    """
    source_dir = project.get_src_dir()
    build_dir  = project.cmake.get_build_dir()

    # Create build dir if it does not exist:
    build_dir = project.cmake.get_build_dir()
    if not os.path.exists(build_dir):
        os.makedirs(build_dir)

    # Always remove CMakeCache and build/sdk/lib/cmake:
    cache = os.path.join(build_dir, "CMakeCache.txt")
    if os.path.exists(cache):
        os.remove(cache)

    qibuild.sh.rm(os.path.join(build_dir, "sdk", "lib", "cmake"))

    # Always specify generator
    cmake_args = ["-G", args.cmake_generator]

    # Append flags from build config, and from command line,
    # if any
    cmake_flags = list()
    if args.cmake_flags:
        cmake_flags.extend(args.cmake_flags)

    cmake_flags.extend(project.cmake.build_config.flags)

    cmake_args.extend(["-D" + flag for flag in cmake_flags])

    # Add path to source:
    cmake_args.append(source_dir)

    qibuild.command.check_call(["cmake"] + cmake_args, cwd=build_dir)



def build_project(args, project):
    r"""Build a project.

    /!\ assumes that set_build_configs has been called
    """
    build_dir = project.cmake.get_build_dir()
    cmd = ["make"]
    if args.num_jobs:
        cmd.append("-j%i" % args.num_jobs)
    if args.target:
        cmd.append(args.target)

    qibuild.command.check_call(cmd, cwd=build_dir)
