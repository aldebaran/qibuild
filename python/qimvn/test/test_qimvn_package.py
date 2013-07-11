import os

import pytest

from qisys.command import CommandFailedException
import qibuild.parsers
from qimvn import jar
from qimvn import deploy
from qimvn import package
from qimvn.test.conftest import add_repository

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction


def get_paths(config=None):
    """ Get project list
    """
    build_worktree = qibuild.parsers.get_build_worktree(None)
    if config:
        build_worktree.set_active_config(config)
    projects = build_worktree.build_projects

    paths = list()
    for proj in projects:
        paths += [proj.sdk_directory]
    return paths

def test_package(qibuild_action, qimvn_action, local_repository):
    """ Test if Maven project is correctly built
    """
    qibuild_action.add_test_project("hellojavajni")
    hellojava = qibuild_action.add_test_project("hellojava")
    add_repository(hellojava, local_repository)
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")
    jar.jar("hellojavajni.jar", ["hellojavajni"], get_paths())
    deploy.deploy("com.test", "1.0-SNAPSHOT", "hellojavajni",
                  "hellojavajni.jar", local_repository)

    assert package.package(hellojava) == 0
    path = hellojava.path
    built_jar = os.path.join(path, "target/hellojava-1.0-SNAPSHOT.jar")
    assert os.path.exists(built_jar)
