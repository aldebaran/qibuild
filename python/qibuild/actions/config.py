## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Display the current config """

import os
import subprocess

import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")

def do(args):
    """Main entry point"""
    toc = None
    try:
        toc = qibuild.toc.toc_open(args.work_tree, args)
    except qibuild.toc.TocException:
        pass

    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()

    if args.edit:
        editor = qibuild_cfg.defaults.env.editor
        if not editor:
            editor = os.environ.get("VISUAL")
        if not editor:
            editor = os.environ.get("EDITOR")
        if not editor:
            # Ask the user to choose, and store the answer so
            # that we never ask again
            print "Could not find the editor to use."
            editor = qibuild.interact.ask_program("Please enter an editor")
            qibuild_cfg.defaults.env.editor = editor
            qibuild_cfg.write()

        full_path = qibuild.command.find_program(editor)
        subprocess.call([full_path, qibuild.config.QIBUILD_CFG_PATH])
        return

    if not toc:
        print qibuild_cfg
        return

    print "General config"
    print "--------------"
    print qibuild.config.indent(str(qibuild_cfg))

    print "Local config"
    print "------------"

    projects = toc.projects
    if projects:
        print "  Projects:"
        for project in projects:
            print qibuild.config.indent(str(project.config), 2)
