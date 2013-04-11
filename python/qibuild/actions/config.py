## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Display the current config """

import subprocess

import qisys
import qibuild
import qibuild.wizard
from qisys import ui

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")
    parser.add_argument("--local", action="store_true", dest="is_local",
        help="only display or edit the local configuration")
    parser.add_argument("--wizard", action="store_true",
        help="run a wizard to edit the configuration")
    parser.set_defaults(local=False)

def do(args):
    """Main entry point"""
    toc = None
    try:
        toc = qibuild.toc.toc_open(args.worktree, args)
    except qisys.worktree.NotInWorktree:
        pass

    if args.wizard:
        qibuild.wizard.run_config_wizard(toc)
        return

    is_local = args.is_local
    if is_local and not toc:
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
            cfg_path = toc.config_path
        else:
            cfg_path = qibuild.config.get_global_cfg_path()
        subprocess.call([full_path, cfg_path])
        return

    if not toc:
        print qibuild_cfg
        return

    if not is_local:
        print "General configuration"
        print "---------------------"
        print ui.indent(str(toc.config))
        print

    print "Local configuration"
    print "-------------------"
    print ui.indent(str(toc.config.local))

    print
    print "Projects configuration"
    print "----------------------"
    projects = toc.projects
    if projects:
        print "  Projects:"
        for project in projects:
            print ui.indent(str(project.config), num=4)
