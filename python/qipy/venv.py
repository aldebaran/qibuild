## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.
import os
import subprocess
import virtualenv

from qisys import ui
import qisys.command

def configure_virtualenv(config, python_worktree,  build_worktree=None,
                         remote_packages=None, site_packages=True):
    """ Main entry point. Called by ``qipy bootstrap``

    :param: remote_packages List of third-party packages to add in the virtualenv
    :param: site_packages Allow access to global site packages

    """
    ui.info(ui.green, "Configuring virtualenv for", ui.reset, ui.bold, python_worktree.root)
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
        return False


    ui.info("Adding python projects")
    # Write a qi.pth file containing path to C/C++ extensions and
    # path to pure python modules or packages
    pure_python_ok = handle_pure_python(venv_path, python_worktree)
    if build_worktree:
        handle_extensions(venv_path, python_worktree, build_worktree)

    ui.info("Adding other requirements: " + ", ".join(remote_packages))
    binaries_path = virtualenv.path_locations(venv_path)[-1]
    pip_binary = os.path.join(binaries_path, "pip")
    remote_ok = True
    if remote_packages:
        cmd = [pip_binary, "install"] + remote_packages
        rc = qisys.command.call(cmd, ignore_ret_code=True)
        remote_ok = (rc == 0)
    if pure_python_ok and remote_ok:
        ui.info(ui.green, "Done")
    if not pure_python_ok:
        ui.info(ui.red, "Failed to add some python projects")
    if not remote_ok:
        ui.info(ui.red, "Failed to add some third party requirements")
    return (pure_python_ok and remote_ok)

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
    """ Check if there is a build project matching the given source, and
    add the correct path to the virtualenv

    """
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
    with open(qi_pth_dest, "a") as fp:
        fp.write(to_write)

def handle_pure_python(venv_path, python_worktree):
    """ Add the paths of all python projects to the virtualenv """
    lib_path = virtualenv.path_locations(venv_path)[1]
    qi_pth_dest = os.path.join(venv_path, lib_path, "site-packages/qi.pth")
    res = True
    with open(qi_pth_dest, "w") as fp:
        fp.write("")
        for project in python_worktree.python_projects:
            if project.setup_with_distutils:
                cmd = [python_worktree.pip, "install", "--editable", "."]
                rc = qisys.command.call(cmd, cwd=project.path, ignore_ret_code=True)
                if rc != 0:
                    ui.warning("Failed to run pip install on", project.src)
                    res = False
            else:
                for path in project.python_path:
                    fp.write(path + "\n")
    return res
