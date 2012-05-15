## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
"""Initialize a new toc worktree """

import os
import logging

import qisrc
import qibuild
import qibuild.wizard

LOGGER = logging.getLogger(__name__)


def configure_parser(parser):
    """Configure parser for this action """
    qibuild.parsers.worktree_parser(parser)
    parser.add_argument("-i", "--interactive", action="store_true",
        help="start a wizard to help you configuring qibuild")
    parser.add_argument("-f", "--force", action="store_true", help="force the init")
    parser.add_argument("-c", "--config",
        help="Choose a default config for this worktree")
    parser.set_defaults(
        cmake_generator="Unix Makefiles")

def do(args):
    """Main entry point"""
    # If user did not specify a worktree, make sure he is not
    # trying to create nested worktrees (there's nothing wrong in
    # having nested worktree, but it may be confusing a little bit)
    if not args.worktree:
        old_worktree = qisrc.worktree.guess_worktree()
        if old_worktree and os.path.exists(old_worktree) and not args.force:
            raise Exception("You already have a qi worktree in : %s.\n" % (old_worktree) +
                        "Use --force if you know what you are doing "
                        "and really want to create a new worktree here.")

    # Use getcwd() if no worktree was given
    worktree = args.worktree
    if not worktree:
        worktree = os.getcwd()

    # Safe to be called: only creates the .qi/ repertory
    qibuild.toc.create(worktree, force=args.force)

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
        return

    qibuild.wizard.run_config_wizard(toc)
