## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Display the current config """

import subprocess

import qisys.parsers
import qibuild.parsers
import qibuild.wizard
from qisys import ui

def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")
    parser.add_argument("--local", action="store_true", dest="is_local",
        help="only display or edit the local configuration")
    parser.add_argument("--wizard", action="store_true",
        help="run a wizard to edit the configuration")
    parser.set_defaults(local=False)

def do(args):
    """Main entry point"""
    worktree = qisys.parsers.get_worktree(args, raises=None)
    if worktree:
        build_worktree = qibuild.worktree.BuildWorkTree(worktree)
    else:
        build_worktree = None

    if args.wizard:
        qibuild.wizard.run_config_wizard(build_worktree=build_worktree)
    else:
        show_config(args, build_worktree)

def show_config(args, build_worktree):

    is_local = args.is_local
    if is_local and not build_worktree:
        ui.fatal("Cannot use --local when not in a worktree")

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read(create_if_missing=True)

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
