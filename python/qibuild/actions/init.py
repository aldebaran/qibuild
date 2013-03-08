## Copyright (c) 2012, 2013 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Initialize a new toc worktree """

import os
import sys

from qisys import ui
import qisys
import qisys.parsers
import qibuild
import qibuild.wizard
import qitoolchain



def configure_parser(parser):
    """Configure parser for this action """
    qisys.parsers.worktree_parser(parser)
    parser.add_argument("-i", "--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")
    parser.add_argument("-f", "--force", action="store_true", help="force the init")
    parser.add_argument("-c", "--config",
        help="Choose a default config for this worktree")
    parser.set_defaults(
        cmake_generator="Unix Makefiles")

def do(args):
    """Main entry point"""

    worktree = args.worktree
    if not worktree:
        worktree = os.getcwd()

    if args.config:
        # Just make sure the user choose a valid default toolchain
        qitoolchain.get_toolchain(args.config)

    worktree = qisys.sh.to_native_path(worktree)
    parent_worktree = qisys.worktree.guess_worktree(worktree)
    if parent_worktree:
        if parent_worktree != worktree:
            # Refuse to create nested worktrees
            ui.error("""A qi worktree already exists in {parent_worktree}
Refusing to create a nested worktree in {worktree}
Use:
    qibuild init -f -w {parent_worktree}
If you want to re-initialize the worktree in {parent_worktree}
""".format(worktree=worktree, parent_worktree=parent_worktree))
            sys.exit(1)
        else:
            # Refuse to re-initalize the worktree unless "-f" is given
            if not args.force:
                ui.warning("There is already a worktree in", worktree, "\n"
                           "Use --force if you want to re-initialize this worktree")
                return

    qisys.worktree.WorkTree(worktree, force=args.force)

    # User maybe re-running qibuild init because it has a
    # bad default exception ...
    try:
        toc = qibuild.toc.toc_open(worktree)
    except qibuild.toc.WrongDefaultException:
        pass

    toc_cfg_path = os.path.join(worktree, ".qi", "qibuild.xml")
    qibuild_cfg = qibuild.config.QiBuildConfig()
    qibuild_cfg.read()
    qibuild_cfg.read_local_config(toc_cfg_path)
    qibuild_cfg.local.defaults.config = args.config
    qibuild_cfg.write_local_config(toc_cfg_path)

    # Safe to be called now that we've created it
    # and that we know we don't have a wrong defaut config:
    toc = qibuild.toc.toc_open(worktree)

    if not args.interactive:
        ui.info(ui.green, "New worktree created in", ui.reset, ui.bold,
                toc.worktree.root)
        return

    qibuild.wizard.run_config_wizard(toc)
