import os
import subprocess
import virtualenv

from qisys import ui
import qisys.command

def configure_virtualenv(config, python_worktree,  build_worktree=None,
                         remote_packages=None):
    if not remote_packages:
        remote_packages = list()

    # create a new virtualenv
    python_worktree.config = config
    venv_path = python_worktree.venv_path
    pip = python_worktree.pip

    virtualenv.create_environment(python_worktree.venv_path)

    # Install all Python projects using pip install -e .
    python_projects = python_worktree.python_projects
    for i, project in enumerate(python_projects):
        ui.info_count(i, len(python_projects),
                     ui.green, "Configuring", ui.reset, ui.blue, project.src)
        cmd = [pip, "install", "--editable", "."]
        qisys.command.call(cmd, cwd=project.path)

    # Write a qi.pth file containing path to C/C++ extensions
    if build_worktree:
        handle_extensions(venv_path, python_worktree, build_worktree)

    # Install the extension in the virtualenv
    binaries_path = virtualenv.path_locations(venv_path)[-1]
    pip_binary = os.path.join(binaries_path, "pip")
    cmd = [pip_binary, "install"] + remote_packages
    subprocess.check_call(cmd)


def handle_extensions(venv_path, python_worktree, build_worktree):
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

    lib_path = virtualenv.path_locations(venv_path)[1]
    qi_pth_dest = os.path.join(venv_path, lib_path, "site-packages/qi.pth")
    with open(qi_pth_dest, "w") as fp:
        fp.write(to_write)
