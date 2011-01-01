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
import logging

import qisrc
import qibuild

def configure_parser(parser):
    """Configure parser for this action """
    qitools.argparsecommand.toc_parser(parser)
    parser.add_argument("name", help="name of the project. (by default the name is deduced from the git url)")

def usage():
    """Overwrite auto-generated usage message"""
    return USAGE

def do(args):
    """Main entry point"""
    qis = qisrc.open(args.work_tree)

    for git_project in qis.git_projects:
        print git_project
    # toc = qibuild.toc.toc_open(args)
    # logger = logging.getLogger(__name__)
    # if args.imported:
    #     src = args.src_or_name
    #     name = os.path.basename(src)
    #     git = Git(src)
    #     remote = git.get_current_remote_url()
    #     # Get the project name from the source dir:
    #     name = os.path.basename(src)
    #     logger.info("adding %s in %s", remote, src)
    #     toc.add(name, url=remote, src=src, imported=True)
    # else:
    #     name = args.src_or_name
    #     url = args.url
    #     logger.info("cloning %s -> %s", url, name)
    #     toc.add(name, url=url)
    #qitools.argparsecommand.run_action("qibuild.actions.toc.load", forward_args=args)


if __name__ == "__main__" :
    import sys
    qitools.argparsecommand.sub_command_main(sys.modules[__name__])
