## Copyright (C) 2011 Aldebaran Robotics
"""Display the current config """

import os

import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)
    qibuild.parsers.build_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")

def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args.work_tree, args, use_env=True)
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
    editor = toc.configstore.get("env", "editor")
    if not editor:
        editor = os.environ.get("VISUAL")
    if not editor:
        editor = os.environ.get("EDITOR")
    if not editor:
        # Ask the user to choose, and store the answer so
        # that we never ask again
        print "Could not find the editor to use."
        editor = qibuild.interact.ask_program("Please enter an editor")
        qibuild.configstore.update_config(config_path, "env", "editor", editor)

    qibuild.command.check_call([editor, config_path])


if __name__ == "__main__" :
    import sys
    qibuild.cmdparse.sub_command_main(sys.modules[__name__])
