## Copyright (C) 2011 Aldebaran Robotics
"""Initialize a new toc worktree """

import os
import logging

import qibuild
import qitoolchain
import qitools
import qitools.cmdparse
import subprocess

LOGGER = logging.getLogger(__name__)


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

    # We only asked for the cmake.flags part of the build configs, so fix this
    # now
    for (name, cmake_flags) in build_configs.iteritems():
        build_configs[name] = dict()
        build_configs[name]["cmake"] = dict()
        build_configs[name]["cmake"]["flags"] = " ".join(cmake_flags)
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
    dot_qi = os.path.join(work_tree, ".qi")
    build_cfg = os.path.join(dot_qi, "build.cfg")
    should_run = False
    if os.path.exists(build_cfg):
        if not args.interactive:
            LOGGER.error("%s already exists, aborting", build_cfg)
            return
        try:
            to_ask  = "%s already exists, do you which to configure it" % build_cfg
            should_run = qitools.ask_yes_no(to_ask)
        except KeyboardInterrupt:
            pass
    else:
        should_run = True

    if not should_run:
        return

    if not os.path.exists(build_cfg):
        qibuild.toc.create(work_tree, args)

    if not args.interactive:
        return

    try:
        run_wizard(build_cfg)
    except KeyboardInterrupt:
        pass

def run_wizard(build_cfg):
    """Write a new configuration if the file passed as
    arguments, asking the user a lot of questions

    """
    old_config = qitools.configstore.ConfigStore()
    old_config.read(build_cfg)
    cmake_generator = ask_cmake_generator()

    default_build_config = None
    new_build_configs = dict()
    if qitools.ask_yes_no("Add custom build configurations"):
        new_build_configs  = ask_build_configs()
    build_configs = old_config.get("build", default=dict())
    build_configs.update(new_build_configs)
    default_build_config = None
    if build_configs:
        default_build_config = qitools.ask_choice(build_configs.keys(),
            "Choose a default build config")

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

    qitools.configstore.update_config(build_cfg,
        "general", "build", "cmake_generator", cmake_generator)
    qitools.configstore.update_config(build_cfg,
        "general", "build", "toolchain", toolchain_name)
    qitools.configstore.update_config(build_cfg,
        "general", "env", "path", env_path)
    if build_configs:
        for name, config in build_configs.iteritems():
            cmake_flags = ""
            cmake = config.get("cmake")
            if cmake:
                cmake_flags = cmake.get("flags")
            qitools.configstore.update_config(build_cfg,
                "build", name, "cmake.flags", cmake_flags)
    if default_build_config:
        qitools.configstore.update_config(build_cfg,
            "general", "build", "build_config", default_build_config)
