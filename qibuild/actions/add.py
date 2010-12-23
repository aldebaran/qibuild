"""Add a new project to the configuration. """

USAGE = """add NAME URL or add --import SOURCES

The project must not already exist

Exemples:
  toc add git://git/foo.git foo
   -> checkout the foo project in src/foo, and update configuration

  toc add --import /path/to/bar
    -> guess the URL from the git project tree, and update configuration
    The /path/to/bar can be an absolute path, or a path relative to
    the work tree
"""

import os
import qibuild
import logging

from qibuild.git  import Git


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.shell.toc_parser(parser)
    parser.add_argument("src_or_name", metavar="SOURCES or NAME",
        help="path to the sources of the project (if --import is given)")
    parser.add_argument("url",  nargs="?", metavar="URL",
        help="git url")
    parser.add_argument("--import", dest="imported", action="store_true",
        help="add an already existing git tree to the toc configuration")

def usage():
    """Overwrite auto-generated usage message"""
    return USAGE


def do(args):
    """Main entry point"""
    toc = qibuild.toc.toc_open(args)
    logger = logging.getLogger(__name__)
    if args.imported:
        src = args.src_or_name
        name = os.path.basename(src)
        git = Git(src)
        remote = git.get_current_remote_url()
        # Get the project name from the source dir:
        name = os.path.basename(src)
        logger.info("adding %s in %s", remote, src)
        toc.add(name, url=remote, src=src, imported=True)
    else:
        name = args.src_or_name
        url = args.url
        logger.info("cloning %s -> %s", url, name)
        toc.add(name, url=url)

    qibuild.shell.run_action("qibuild.actions.toc.load", forward_args=args)


if __name__ == "__main__" :
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])
