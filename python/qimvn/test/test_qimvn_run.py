import pytest
import os

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qimvn import jar
from qimvn import deploy
from qimvn import package
from qimvn import run
from qisys.command import CommandFailedException

def test_package(qibuild_action):
    """ Test if Maven project is correctly built
    """
    qibuild_action.add_test_project("hellojavajni")
    qibuild_action.add_test_project("hellojava")
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")

    qibuild_action.package = "qimvn.actions"
    qibuild_action("jar", "hellojavajni.jar", "hellojavajni")
    qibuild_action("deploy", "hellojavajni.jar", "--groupId", "com.test",
                   "--version", "1.0-SNAPSHOT", "--artifactId", "hellojavajni",
                   "--url", "file:///tmp/maven/")
    qibuild_action("package", "hellojava")

    worktree = qibuild_action.build_worktree.worktree
    assert run.run(worktree.projects, "hellojava") == 0

def test_package_action(qibuild_action):
    """ Test if Maven project is correctly built
    """
    qibuild_action.add_test_project("hellojavajni")
    qibuild_action.add_test_project("hellojava")
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")

    qibuild_action.package = "qimvn.actions"
    qibuild_action("jar", "hellojavajni.jar", "hellojavajni")
    qibuild_action("deploy", "hellojavajni.jar", "--groupId", "com.test",
                   "--version", "1.0-SNAPSHOT", "--artifactId", "hellojavajni",
                   "--url", "file:///tmp/maven/")
    qibuild_action("package", "hellojava")

    assert qibuild_action("run", "hellojava") == 0