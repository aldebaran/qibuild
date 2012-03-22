## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Display the current config """

import os
import subprocess

import qibuild
import qibuild.wizard

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")
    parser.add_argument("--wizard", action="store_true",
        help="run a wizard to edit the configuration")

def do(args):
    """Main entry point"""
    toc = None
    try:
        toc = qibuild.toc.toc_open(args.worktree, args)
    except qibuild.toc.TocException:
        pass

    if args.wizard:
        qibuild.wizard.run_config_wizard(toc)
        return

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()

    if args.edit:
        editor = qibuild_cfg.defaults.env.editor
        if not editor:
            editor = qibuild.interact.get_editor()
            qibuild_cfg.defaults.env.editor = editor
            qibuild_cfg.write()

        full_path = qibuild.command.find_program(editor)
        subprocess.call([full_path, qibuild.config.get_global_cfg_path()])
        return

    if not toc:
        print qibuild_cfg
        return

    print "General configuration"
    print "---------------------"
    print qibuild.config.indent(str(toc.config))
    print

    print "Local configuration"
    print "-------------------"
    print qibuild.config.indent(str(toc.config.local))

    print
    print "Projects configuration"
    print "----------------------"
    projects = toc.projects
    if projects:
        print "  Projects:"
        for project in projects:
            print qibuild.config.indent(str(project.config), 2)
