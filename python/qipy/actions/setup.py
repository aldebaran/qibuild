""" Make all python projects available in the current build configuartion

"""
import sys
import os

from qisys import ui
import qisys.sh
import qisys.command
import qisys.parsers
import qibuild.parsers
import qipy.parsers
import qipy.worktree

def configure_parser(parser):
    qibuild.parsers.build_parser(parser)
    # FIXME: add -r
    parser.add_argument("requirements", nargs="*")

def do(args):
    build_worktree = qibuild.parsers.get_build_worktree(args)
    build_config = qibuild.parsers.get_build_config(build_worktree, args)
    build_worktree.build_config = build_config
    worktree = build_worktree.worktree
    python_worktree = qipy.parsers.get_python_worktree(args)
    config = build_config.active_config
    if not config:
        config = "system"

    # create a new virtualenv
    venv_root = python_worktree.venv_path(config)

    try:
        import virtualenv
    except ImportError:
        ui.error("Please install virtualenv to use `qipy setup`")
        raise

    virtualenv.create_environment(venv_root)
    bin_path = virtualenv.path_locations(venv_root)[-1]
    pip = os.path.join(bin_path, "pip")

    handle_requirements(venv_root, args.requirements)

    python_projects = python_worktree.python_projects
    for i, project in enumerate(python_projects):
        ui.info_count(i, len(python_projects),
                     ui.green, "Installing from worktree", ui.reset, ui.blue, project.src)
        cmd = [pip, "install", "--editable", "."]
        qisys.command.call(cmd, cwd=project.path)

    handle_extensions(venv_root, python_worktree, build_worktree)


def handle_extensions(venv_root, python_worktree, build_worktree):
    """ Check if there is a build project matching the given source """
    extensions_projects = list()
    build_projects = build_worktree.build_projects
    for project in python_worktree.python_projects:
        matching_build_project = None
        for build_project in build_projects:
            if build_project.src == project.src:
                extensions_projects.append(build_project)

    to_write = ""
    for project in extensions_projects:
        qi_pth_src = os.path.join(project.sdk_directory, "qi.pth")
        if os.path.exists(qi_pth_src):
            with open(qi_pth_src, "r") as fp:
                to_write += fp.read()
                if not to_write.endswith("\n"):
                    to_write += "\n"

    qi_pth_dest = os.path.join(venv_root, "lib/python2.7/site-packages/qi.pth")
    with open(qi_pth_dest, "w") as fp:
        fp.write(to_write)

def handle_requirements(venv_root, requirements):
    # FIXME: add python_worktree.pip
    import virtualenv
    bin_path = virtualenv.path_locations(venv_root)[-1]
    pip = os.path.join(bin_path, "pip")
    for (i, requirement) in enumerate(requirements):
        ui.info_count(i, len(requirements),
                      "Installing requirement", requirement)
        cmd = [pip, "install", requirement]
        qisys.command.call(cmd)
