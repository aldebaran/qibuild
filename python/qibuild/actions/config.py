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
    toc = qibuild.toc.toc_open(args.work_tree, args)
    if not args.edit:
        if toc.active_config:
            print "Active configuration:"
            print " ", toc.active_config
            print
        print "Build configurations:"
        print toc.configstore
        print
        print "Projects configuration:"
        for project in toc.projects:
            print project.configstore


    if not args.edit:
        return

    config_path = qibuild.configstore.get_config_path()
    editor = toc.configstore.get("env.editor")
    if not editor:
        editor = os.environ.get("VISUAL")
    if not editor:
        editor = os.environ.get("EDITOR")
    if not editor:
        # Ask the user to choose, and store the answer so
        # that we never ask again
        print "Could not find the editor to use."
        editor = qibuild.interact.ask_program("Please enter an editor")
        qibuild.configstore.update_config(config_path, "general", "env.editor", editor)

    full_path = qibuild.command.find_program(editor)
    subprocess.call([full_path, toc.config_path])
    qibuild.command.call([editor, config_path])

