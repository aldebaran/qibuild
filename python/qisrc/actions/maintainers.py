## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Manage the list of maintainers."""

from qisys import ui
import qisys.parsers
import qisrc.cmdparse
import qisrc.git
import qisrc.maintainers

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser, positional=False)
    parser.add_argument("--list", action="store_true", help="List all the maintainers")
    parser.add_argument("--remove", action="store_true", help="Remove maintainers")
    parser.add_argument("--clear", action="store_true", help="Remove all maintainers")

def do(args):
    """Main entry point."""

    worktree = qisys.worktree.open_worktree(args.worktree)
    projects = qisrc.cmdparse.projects_from_args(args, worktree)

    # Parse list of maintainers

    for project in projects:
        if args.remove:
            maintainers = qisrc.maintainers.get(project)
            if len(maintainers) == 0:
                ui.info("There is no maintainer currently.")
                continue
            maintainers_string = ["None"]
            maintainers_string.extend([qisrc.maintainers.to_str(**x) for x in maintainers])
            num = qisys.interact.ask_choice(maintainers_string, "Which one do you want remove?", return_int=True)
            if num == 0:
                continue
            maintainer = maintainers[num-1]
            qisrc.maintainers.remove(project, **maintainer)
            ui.info(ui.blue, qisrc.maintainers.to_str(**maintainer),
                    ui.reset, "remove from maintainers")
            continue

        if args.clear:
            if qisrc.maintainers.clear(project):
                ui.info("All maintainers removed")
            else:
                ui.info("There is no maintainer for this project")
            continue

        # Fallback => list
        maintainers = qisrc.maintainers.get(project)

        if len(maintainers) > 0:
            ui.info("Maintainers of", ui.green, project.src)
        else:
            ui.info("There is no maintainer configured for this project.")
        for maintainer in maintainers:
            maintainer_string = qisrc.maintainers.to_str(**maintainer)
            ui.info("  ", ui.green, "* ", ui.reset, maintainer_string)
