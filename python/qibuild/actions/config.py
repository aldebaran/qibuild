## Copyright (C) 2011 Aldebaran Robotics
"""Display the current config """

import os

import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.qiworktree.work_tree_parser(parser)
    parser.add_argument("--edit", action="store_true",
        help="edit the configuration")

def do(args):
    """Main entry point"""
    qiwt = qibuild.qiworktree_open(args.work_tree, use_env=True, config=args.config)
    if not args.edit:
        print qiwt.configstore
        return

    config_path = qiwt.user_config_path
    editor = qiwt.configstore.get("general", "env", "editor")
    if not editor:
        editor = os.environ.get("VISUAL")
    if not editor:
        editor = os.environ.get("EDITOR")
    if not editor:
        # Ask the user to choose, and store the answer so
        # that we never ask again
        print "Could not find the editor to use."
        editor = qibuild.interact.ask_program("Please enter an editor")
        qibuild.configstore.update_config(config_path,
            "general", "env", "editor", editor)

    qibuild.command.check_call([editor, config_path])


if __name__ == "__main__" :
    import sys
    qibuild.cmdparse.sub_command_main(sys.modules[__name__])
