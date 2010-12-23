"""Display the current config """

import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qibuild.shell.toc_parser(parser)


def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args)
    print toc.configstore

if __name__ == "__main__" :
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])
