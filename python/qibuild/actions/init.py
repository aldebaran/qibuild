## Copyright (C) 2011 Aldebaran Robotics
"""Initialize a new toc worktree """

import os
import qibuild
import qitoolchain
import qitools
import qitools.cmdparse
import subprocess


def ask_cmake_generator():
    """Ask the user to choose a cmake generator """
    cmake_process = subprocess.Popen(["cmake"], stdout=subprocess.PIPE)
    (out, _err) = cmake_process.communicate()
    lines = out.splitlines()
    interesting_lines = list()
    interesting = False
    for line in lines:
        if line == "Generators":
            interesting = True
            continue
        if interesting and line:
           interesting_lines.append(line)

    generators = list()
    for line in interesting_lines:
        if " = " in line:
            generator = line.split("=")[0]
            generator = generator.strip()
            if generator:
                generators.append(generator)

    generator = qitools.ask_choice(generators, "Choose a CMake generator:")
    return generator


def ask_toolchain():
    """Ask the user to choose a toolchain name"""

    config_file = qitoolchain.get_config_path()
    config = qitools.configstore.ConfigStore()
    config.read(config_file)
    toolchain_dict = config.get("toolchain", default=dict())
    toolchain_names = toolchain_dict.keys()
    return qitools.ask_choice(toolchain_names, "Choose a toolchain name")


def ask_build_configs():
    """Ask the user to choose build configurations"""
    keep_going = True
    build_configs = dict()
    while keep_going:
        print ":: Choose a build configuration name: "
        build_config_name = raw_input("> ")
        if not build_config_name:
            keep_going = False
            continue
        build_configs[build_config_name] = list()
        keep_asking_flags=True
        while keep_asking_flags:
            print ":: Flags for %s build config (name=value)" % build_config_name
            flags = raw_input("> ")
            if not flags:
                keep_asking_flags = False
                continue
            if not "=" in flags:
                print "invalid flags"
                continue
            splitted = flags.split("=")
            if len(splitted) != 2:
                print "invalid flags"
                continue
            build_configs[build_config_name].append(flags)
            if qitools.ask_yes_no("Done with %s build config" % build_config_name):
                keep_asking_flags = False
            continue

        keep_going = qitools.ask_yes_no("Add a new build config")

    return build_configs

def ask_path():
    """Ask the user to choose paths to be added to
    os.environ[PATH]

    """
    paths = list()
    keep_going = True
    while keep_going:
        print ":: Select a new path to be added to os.environ"
        path = raw_input("> ")
        if not path:
            keep_going = False
            continue
        paths.append(path)
        keep_going = qitools.ask_yes_no("A a new path to os.environ")
    # configuration file expects paths separated pathsep
    return os.path.pathsep.join(paths)

def ask_default_build_config(build_configs):
    """Ask the user to choose a default build config"""
    return qitools.ask_choice(build_configs.keys(),
        "Select a default build config")

def create_toolchain():
    """Ask the use for a toolchain name and create one"""
    print ":: Choose a toolchain name"
    answer = raw_input("> ")
    qitools.run_action("qitoolchain.actions.create", [answer])
    return answer

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    parser.add_argument("--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")

def do(args):
    """Main entry point"""
    work_tree = qitools.qiworktree.worktree_from_args(args)
    qiworktree = qitools.qiworktree_open(work_tree)
    dot_qi = os.path.join(qiworktree.work_tree, ".qi")

    if not os.path.isdir(dot_qi):
        qibuild.toc.create(work_tree, args)

    if not args.interactive:
        return

    build_cfg = os.path.join(dot_qi, "build.cfg")
    if os.path.exists(build_cfg):
        to_ask  = "%s already exists, do you which to configure it" % build_cfg
        if not qitools.ask_yes_no(to_ask):
            return

    try:
        run_wizard(qiworktree)
    except KeyboardInterrupt:
        # Remove the half-configured config file,
        # so that the user can re-run the wizard again:
        qitools.sh.rm(build_cfg)

def run_wizard(qiworktree):
    cmake_generator = ask_cmake_generator()

    default_build_config = None
    build_configs = dict()
    if qitools.ask_yes_no("Define custom build configurations"):
        build_configs  = ask_build_configs()
    if build_configs:
        default_build_config = ask_default_build_config(build_configs)

    toolchain_name = None
    if qitools.ask_yes_no("Use a toolchain"):
        tc_config = qitoolchain.get_config_path()
        if not os.path.exists(tc_config):
            if qitools.ask_yes_no("No toolchain found, crate one"):
                toolchain_name = create_toolchain()
        else:
            toolchain_name = ask_toolchain()

    env_path = ""
    if qitools.ask_yes_no("Use custom environment"):
        env_path       = ask_path()

    qiworktree.update_config(
        "general", "build", "cmake_generator", cmake_generator)
    qiworktree.update_config(
        "general", "build", "toolchain", toolchain_name)
    qiworktree.update_config(
        "general", "env", "path", env_path)
    if build_configs:
        for name, flags in build_configs.iteritems():
            qiworktree.update_config(
            "build", name, "cmake.flags", flags)
        qiworktree.update_config(
            "general", "build", "build_config", default_build_config)
