"""Display the current config """

import qibuild
import qitools.argparsecommand

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.toc_parser(parser)

def do(args):
    """Main entry point"""
    toc = qibuild.toc.open(args.work_tree, use_env=True)
    print toc.configstore

if __name__ == "__main__" :
    import sys
    qitools.argparsecommand.sub_command_main(sys.modules[__name__])
