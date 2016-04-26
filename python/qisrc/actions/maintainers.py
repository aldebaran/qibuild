## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

"""Manage the list of maintainers."""

from qisys import ui
import qisys.parsers
import qisrc.git
import qisrc.maintainers

def configure_parser(parser):
    """Configure parser for this action."""
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser, positional=False)
    group = parser.add_argument_group("qisrc maintainers options")
    group.add_argument("--add", action="store_const",
                        dest="maintainers_action", const="add",
                        help="Add a new maintainer")
    group.add_argument("--list", action="store_const",
                        dest="maintainers_action", const="list",
                        help="List all the maintainers")
    group.add_argument("--remove", action="store_const",
                        dest="maintainers_action", const="remove",
                        help="Remove maintainers")
    group.add_argument("--clear", action="store_const",
                        dest="maintainers_action", const="clear",
                        help="Remove all maintainers")
    group.add_argument("--name",
                       help="Name of the maintainer to add or remove")
    group.add_argument("--email",
                       help="email of the maintainer to add or remove")
    parser.set_defaults(maintainers_action="list")

def do(args):
    """Main entry point."""

    worktree = qisys.parsers.get_worktree(args)
    projects = qisys.parsers.get_projects(worktree, args)

    if not projects:
        ui.fatal("Please specify at least one project")

    if args.maintainers_action == "add":
        to_call = add_maintainer
    if args.maintainers_action == "list":
        to_call = list_maintainers
    elif args.maintainers_action == "remove":
        to_call = remove_maintainer
    elif args.maintainers_action == "clear":
        to_call = clear_maintainers

    for project in projects:
        to_call(project, args)

def add_maintainer(project, args):
    name = args.name
    if not name:
        name = qisys.interact.ask_string("name: ")
        if not name:
            return
    email = args.email
    if not email:
        email = qisys.interact.ask_string("email: ")
        if not email:
            return
    qisrc.maintainers.add(project, name=name, email=email)



def remove_maintainer(project, args):
    maintainers = qisrc.maintainers.get(project)
    if not maintainers:
        ui.info("No maintainer configured for this project")
        return
    maintainers_string = ["None"]
    maintainers_string.extend(
        [qisrc.maintainers.to_str(**x) for x in maintainers])
    num = qisys.interact.ask_choice(maintainers_string,
                                    "Which one do you want remove?",
                                    return_int=True)
    if num == 0:
        return
    maintainer = maintainers[num-1]
    qisrc.maintainers.remove(project, **maintainer)
    ui.info(ui.blue, qisrc.maintainers.to_str(**maintainer),
            ui.reset, "removed from maintainers")

def clear_maintainers(project, *unused_args):
    if qisrc.maintainers.clear(project):
        ui.info("All maintainers removed")
    else:
        ui.info("No maintainer configured for this project")


def list_maintainers(project, *unused_args):
    maintainers = qisrc.maintainers.get(project)

    if maintainers:
        ui.info("Maintainers of", ui.green, project.src)
    else:
        ui.info("No maintainer configured for", ui.green, project.src)
    for maintainer in maintainers:
        maintainer_string = qisrc.maintainers.to_str(**maintainer)
        ui.info("  ", ui.green, "* ", ui.reset, maintainer_string)
