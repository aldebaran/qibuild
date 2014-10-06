import os
import subprocess
import virtualenv

from qisys import ui
import qisys.command

def configure_virtualenv(config, python_worktree,  build_worktree=None,
                         remote_packages=None, site_packages=True):
    if not remote_packages:
        remote_packages = list()

    # create a new virtualenv
    python_worktree.config = config
    venv_path = python_worktree.venv_path
    pip = python_worktree.pip

    try:
        virtualenv.create_environment(python_worktree.venv_path,
                                      site_packages=site_packages)
    except:
        ui.error("Failed to create virtualenv")
        return

    # Install all Python projects using pip install -e .
    python_projects = python_worktree.python_projects
    for i, project in enumerate(python_projects):
        ui.info_count(i, len(python_projects),
                     ui.green, "Configuring", ui.reset, ui.blue, project.src)
        cmd = [pip, "install", "--editable", "."]
        rc = qisys.command.call(cmd, cwd=project.path, ignore_ret_code=True)
        if rc != 0:
            ui.warning("Running pip install -e failed for project", project.src)

    # Write a qi.pth file containing path to C/C++ extensions
    if build_worktree:
        handle_extensions(venv_path, python_worktree, build_worktree)

    # Install the extension in the virtualenv
    binaries_path = virtualenv.path_locations(venv_path)[-1]
    pip_binary = os.path.join(binaries_path, "pip")
    if remote_packages:
        cmd = [pip_binary, "install"] + remote_packages
        subprocess.check_call(cmd)

def find_script(venv_path, script_name):
    """ Find a script given its name

    First try in the virtualenv, then from $PATH
    :return: None if not found

    """
    binaries_path = virtualenv.path_locations(venv_path)[-1]
    if os.name == 'nt':
        candidate = os.path.join(binaries_path,
                                 script_name + ".exe")
    else:
        candidate = os.path.join(binaries_path, script_name)
    if os.path.exists(candidate):
        return candidate
    res = qisys.command.find_program(script_name)
    if res:
        return res

def handle_extensions(venv_path, python_worktree, build_worktree):
    """ Check if there is a build project matching the given source """
    extensions_projects = list()
    build_projects = build_worktree.build_projects
    for project in python_worktree.python_projects:
        parent_project = qisys.parsers.find_parent_project(build_projects,
                                                           project.path)
        if parent_project:
            extensions_projects.append(parent_project)

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
