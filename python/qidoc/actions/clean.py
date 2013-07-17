""" Clean the build-doc directory

"""

import os

from qisys import ui
import qisys.sh
import qisys.parsers
import qidoc.parsers
import qidoc.builder

def configure_parser(parser):
    qisys.parsers.worktree_parser(parser)
    qisys.parsers.project_parser(parser)
    group = parser.add_argument_group("qidoc clean options")
    group.add_argument("-f", "--force", help="force the clean",
                        action="store_true")


def do(args):
    doc_worktree = qidoc.parsers.get_doc_worktree(args)
    doc_projects = qidoc.parsers.get_doc_projects(doc_worktree, args)

    to_clean = list()
    for doc_project in doc_projects:
        # FIXME
        # this can create an empty build dir for nothing, so
        # we remove it if we don't need it
        build_dir = doc_project.build_dir
        if not os.path.exists(build_dir):
            continue
        if qisys.sh.is_empty(build_dir):
            qisys.sh.rm(build_dir)
            continue
        to_clean.append(build_dir)

    if not to_clean:
        ui.info(ui.green, "Nothing to clean")
        return

    if not args.force:
        ui.info(ui.green, "Build directories that will be removed",
                ui.white, "(use -f to apply")

    for i, build_dir in enumerate(to_clean):
        if args.force:
            ui.info_count(i, len(to_clean),
                          ui.green, "Cleaning", ui.reset,
                          build_dir)
            qisys.sh.rm(build_dir)
        else:
            ui.info_count(i, len(to_clean), build_dir)
