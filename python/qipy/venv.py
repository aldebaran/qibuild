# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os
import sys
import virtualenv

from qisys import ui
import qisys.command


def _create_virtualenv(config, python_worktree, site_packages=True, python_executable=None, env=None):
    python_worktree.config = config
    venv_path = python_worktree.venv_path
    # pip = python_worktree.pip

    if not python_executable:
        python_executable = sys.executable
    virtualenv_py = virtualenv.__file__
    if virtualenv_py.endswith(".pyc"):
        virtualenv_py = virtualenv_py[:-1]
    cmd = [python_executable, virtualenv_py, venv_path]
    if site_packages:
        cmd.append("--system-site-packages")
    try:
        qisys.command.call(cmd, env=env)
    except qisys.command.CommandFailedException:
        ui.error("Failed to create virtualenv")
        return False

    binaries_path = virtualenv.path_locations(venv_path)[-1]
    pip_binary = os.path.join(binaries_path, "pip")

    return pip_binary, venv_path


def _update_pip(pip_binary, remote_packages, env):
    cmd = [pip_binary, "install", "--upgrade", "pip"]
    if remote_packages and "pip" in remote_packages:
        remote_packages.remove("pip")
    qisys.command.call(cmd, env=env)


def configure_virtualenv(config, python_worktree, build_worktree=None,
                         remote_packages=None, site_packages=True,
                         python_executable=None, env=None):
    # pylint: disable=too-many-branches,too-many-locals
    """ Main entry point. Called by ``qipy bootstrap``

    :param: remote_packages List of third-party packages to add in the virtualenv
    :param: site_packages Allow access to global site packages

    """
    ui.info(ui.green, "Configuring virtualenv for", ui.reset, ui.bold, python_worktree.root)
    if not remote_packages:
        remote_packages = list()

    # create a new virtualenv
    pip_binary, venv_path = _create_virtualenv(
        config, python_worktree,
        site_packages=site_packages, python_executable=python_executable, env=env)

    # Upgrade pip separately, because old versions may cause install errors
    try:
        _update_pip(pip_binary, remote_packages, env)
    except qisys.command.CommandFailedException:
        ui.error("Failed to upgrade pip")
        return False

    ui.info(ui.blue, "::", ui.reset, "Adding python projects")
    # Write a qi.pth file containing path to C/C++ extensions and
    # path to pure python modules or packages
    pure_python_ok = handle_pure_python(venv_path, python_worktree, env=env)
    if build_worktree:
        handle_extensions(venv_path, python_worktree, build_worktree)
    handle_modules(venv_path, python_worktree)
    ui.info()

    ui.info(ui.blue, "::", ui.reset,
            "Adding other requirements: " + ", ".join(remote_packages))
    remote_ok = True
    if remote_packages:
        cmd = [pip_binary, "install"]
        if not ui.CONFIG["verbose"]:
            cmd.append("--quiet")
        cmd.extend(remote_packages)
        rc = qisys.command.call(cmd, ignore_ret_code=True, env=env)
        remote_ok = (rc == 0)
    if not pure_python_ok:
        ui.info(ui.red, "Failed to add some python projects")
    if not remote_ok:
        ui.info(ui.red, "Failed to add some third party requirements")

    ui.info()
    projects_with_requirements = list()
    for project in python_worktree.python_projects:
        path = os.path.join(project.path, "requirements.txt")
        if os.path.isfile(path):
            projects_with_requirements.append(project)

    ui.info(ui.blue, "::", ui.reset,
            "Installing deps from requirements.txt files")
    requirements_ok = True
    for i, project in enumerate(projects_with_requirements):
        ui.info_count(i, len(projects_with_requirements),
                      ui.blue, project.name)
        cmd = [pip_binary, "install"]
        if not ui.CONFIG["verbose"]:
            cmd.append("--quiet")
        path = os.path.join(project.path, "requirements.txt")
        cmd.extend(["--requirement", path])
        rc = qisys.command.call(cmd, ignore_ret_code=True, env=env)
        requirements_ok = (rc == 0)
    ui.info()
    res = (pure_python_ok and remote_ok and requirements_ok)
    if res:
        ui.info(ui.green, "Done")
    else:
        ui.error("Bootstrap failed")
    return res


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

    if extensions_projects:
        ui.info()
        ui.info(ui.blue, "::", ui.reset, "Registering C++ extensions")
    to_write = ""
    for i, project in enumerate(extensions_projects):
        ui.info_count(i, len(extensions_projects),
                      ui.blue, project.name)
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


def handle_pure_python(venv_path, python_worktree, env=None):
    """ Add the paths of all python projects to the virtualenv """
    lib_path = virtualenv.path_locations(venv_path)[1]
    qi_pth_dest = os.path.join(venv_path, lib_path, "site-packages/qi.pth")
    res = True
    with open(qi_pth_dest, "w") as fp:
        fp.write("")
        for i, project in enumerate(python_worktree.python_projects):
            ui.info_count(i, len(python_worktree.python_projects),
                          ui.blue, project.name)
            if project.setup_with_distutils:
                cmd = [python_worktree.pip, "install"]
                if not ui.CONFIG["verbose"]:
                    cmd.append("--quiet")
                cmd.extend(["--editable", "."])
                rc = qisys.command.call(cmd, cwd=project.path, ignore_ret_code=True,
                                        env=env)
                if rc != 0:
                    ui.warning("Failed to run pip install on", project.src)
                    res = False
            else:
                ui.debug("Adding python path for project", project.name, ":\n",
                         project.python_path)
                for path in project.python_path:
                    fp.write(path + "\n")
    return res


def handle_modules(venv_path, python_worktree):
    """ Register the qi modules by writing the .mod file in the correct location """
    qimodules = list()
    for project in python_worktree.python_projects:
        for module in project.modules:
            if module.qimodule:
                qimodules.append(module)
        for package in project.packages:
            if package.qimodule:
                qimodules.append(package)
    if qimodules:
        ui.info()
        ui.info(ui.blue, "::", ui.reset, "Registering Python qi modules")
    for i, qimodule in enumerate(qimodules):
        ui.info_count(i, len(qimodules), ui.blue, qimodule.name)
        to_make = os.path.join(venv_path, "share", "qi", "module")
        qisys.sh.mkdir(to_make, recursive=True)
        to_write = os.path.join(to_make, "%s.mod" % qimodule.name)
        with open(to_write, "w") as fp:
            fp.write("python\n")
