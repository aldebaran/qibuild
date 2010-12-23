"""Load project configurations """

import os
import qibuild
import logging

LOGGER = logging.getLogger(__name__)

def configure_parser(parser):
    """Configure parser for this action"""
    qibuild.shell.toc_parser(parser)

def _load(toc):
    """Load projects, cloning projects if they do not
    exist

    """
    for project in toc.get_projects():
        src_dir = project.get_src_dir()
        url = project.config.get("git.url")
        if url is None:
            LOGGER.warning("No URL found for %s, skipping.",
                str(project))
            continue
        if not os.path.exists(src_dir):
            parent = os.path.abspath(os.path.join(src_dir, ".."))
            if not os.path.exists(parent):
                os.makedirs(parent)
            LOGGER.info("Cloning: %s -> %s", url, src_dir)
            project.git.clone(url, src_dir)

def _recursive_load(toc):
    """Load project dependencies

    This is recursive because a new dep can also have
    its own dependencies :)

    """
    prevdbprojs = toc.config.get("project")
    dbprojs = list()

    i = 0
    while dbprojs != prevdbprojs and i < 1000:
        _load(toc)
        toc.load(use_env=True, use_cwd=True)
        prevdbprojs = dbprojs
        dbprojs = toc.config.get("project")
    if i >= 1000:
        raise Exception("aie aie aie")


def do(args):
    """Main entry point """
    toc = qibuild.toc.toc_open(args)
    _recursive_load(toc)



if __name__ == "__main__":
    import sys
    qibuild.shell.sub_command_main(sys.modules[__name__])
