## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Display the current config """

import subprocess

import qisys
import qibuild.parsers
import qibuild.wizard
from qisys import ui

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.cmake_build_parser(parser)
    subparsers = parser.add_subparsers(dest="config_action", title="actions")

    add_parser = subparsers.add_parser("add")
    add_parser.add_argument("name")
    add_parser.add_argument("-t", "--toolchain", dest="toolchain")
    add_parser.add_argument("-p", "--profile", dest="profiles", action="append")
    add_parser.add_argument("--ide")
    add_parser.add_argument("-G", "--cmake-generator", dest="cmake_generator")
    add_parser.add_argument("--default", action="store_true")
    add_parser.set_defaults(default=False)

    remove_parser = subparsers.add_parser("remove")
    remove_parser.add_argument("name")

    show_parser = subparsers.add_parser("show")
    show_parser.add_argument("--edit", action="store_true",
        help="edit the configuration")
    show_parser.add_argument("--local", action="store_true", dest="is_local",
        help="only display or edit the local configuration")
    show_parser.set_defaults(local=False)

    wizard_parser = subparsers.add_parser("wizard")

def do(args):
    """Main entry point"""
    build_worktree = None
    try:
        build_worktree = qibuild.parsers.get_build_worktree(args)
    except qisys.worktree.NotInWorkTree:
        pass

    if args.config_action == "wizard":
        qibuild.wizard.run_config_wizard(build_worktree)
        return

    if args.config_action == "show":
        show_config(args, build_worktree)
        return

    if args.config_action == "add":
        add_config(args, build_worktree)
        return

    if args.config_action == "remove":
        remove_config(args)

def show_config(args, build_worktree):

    is_local = args.is_local
    if is_local and not build_worktree:
        raise Exception("Cannot use --local when not in a worktree")

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()

    if args.edit:
        editor = qibuild_cfg.defaults.env.editor
        if not editor:
            editor = qisys.interact.get_editor()
            qibuild_cfg.defaults.env.editor = editor
            qibuild_cfg.write()

        full_path = qisys.command.find_program(editor)
        if is_local:
            cfg_path = build_worktree.qibuild_xml
        else:
            cfg_path = qibuild.config.get_global_cfg_path()
        subprocess.call([full_path, cfg_path])
        return

    if not build_worktree:
        print qibuild_cfg
        return

    if not is_local:
        print "General configuration"
        print "---------------------"
        print ui.indent(str(qibuild_cfg))
        print

    print "Local configuration"
    print "-------------------"
    print ui.indent(str(qibuild_cfg.local))

def add_config(args, build_worktree):
    name = args.name
    toolchain = args.toolchain
    profiles = args.profiles
    ide = args.ide
    cmake_generator = args.cmake_generator
    qibuild.config.add_build_config(name, toolchain=toolchain, profiles=profiles,
                                    ide=ide, cmake_generator=cmake_generator)
    if args.default:
        if not build_worktree:
            raise Exception("Must be in a worktree to use --default")
        build_worktree.set_default_config(name)

def remove_config(args):
    name = args.name
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    del qibuild_cfg.configs[name]

    # Also remove default config from global qibuild.xml file, so
    # that we don't get a default config pointing to a non-existing
    # config
    for worktree in qibuild_cfg.worktrees.values():
        if worktree.defaults.config == name:
            qibuild_cfg.set_default_config_for_worktree(worktree.path, None)
    qibuild_cfg.write()
