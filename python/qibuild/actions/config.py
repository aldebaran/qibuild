"""Display the current config """

import qitools

def configure_parser(parser):
    """Configure parser for this action """
    qitools.qiworktree.work_tree_parser(parser)

def do(args):
    """Main entry point"""
    qiwt = qitools.qiworktree.open(args.work_tree, use_env=True)
    print qiwt.configstore

if __name__ == "__main__" :
    import sys
    qitools.cmdparse.sub_command_main(sys.modules[__name__])
