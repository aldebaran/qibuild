import pytest
import os

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qimvn.test.conftest import add_repository
from qimvn import jar
from qimvn import deploy
from qimvn import package
from qimvn import run
from qisys.command import CommandFailedException

def test_package(qibuild_action, local_repository):
    """ Test if Maven project is correctly built
    """
    qibuild_action.add_test_project("hellojavajni")
    hellojava_proj = qibuild_action.add_test_project("hellojava")
    add_repository(hellojava_proj, local_repository)
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")

    qibuild_action.package = "qimvn.actions"
    qibuild_action("jar", "hellojavajni.jar", "hellojavajni")
    qibuild_action("deploy", "hellojavajni.jar", "--groupId", "com.test",
                   "--version", "1.0-SNAPSHOT", "--artifactId", "hellojavajni",
                   "--url", local_repository)

    qibuild_action("package", "hellojava")

    worktree = qibuild_action.build_worktree.worktree
    assert run.run(worktree.projects, "hellojava") == 0

def test_package_action(qibuild_action, local_repository):
    """ Test if Maven project is correctly built
    """
    qibuild_action.add_test_project("hellojavajni")
    hellojava_proj = qibuild_action.add_test_project("hellojava")
    add_repository(hellojava_proj, local_repository)
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")

    qibuild_action.package = "qimvn.actions"
    qibuild_action("jar", "hellojavajni.jar", "hellojavajni")
    qibuild_action("deploy", "hellojavajni.jar", "--groupId", "com.test",
                   "--version", "1.0-SNAPSHOT", "--artifactId", "hellojavajni",
                   "--url", local_repository)
    qibuild_action("package", "hellojava")

    assert qibuild_action("run", "hellojava") == 0
