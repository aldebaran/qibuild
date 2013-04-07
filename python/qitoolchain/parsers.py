import qisys.worktree
import qibuild.parsers

import qitoolchain

def get_toolchain(args):
    """ Get the toolchain to use.
    If we are inside a build worktree, return the default
    toolchain is this worktree

    """
    config = args.config
    if not config:
        try:
            build_worktree = qibuild.parsers.get_build_worktree(args)
            config = build_worktree.build_config.active_config
        except qisys.worktree.NotInWorkTree:
            config = None

    if not config:
        mess  = "Could not find which config to use.\n"
        mess += "(not in a work tree or no default config in "
        mess += "current worktree configuration)\n"
        mess += "Please specify a configuration with -c \n"
        raise Exception(mess)

    return qitoolchain.get_toolchain(config)
