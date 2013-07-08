import pytest
import os

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qimvn import jar
from qimvn import deploy
from qimvn import package
from qisys.command import CommandFailedException

def test_package(qibuild_action, qimvn_action):
    """ Test if Maven project is correctly built
    """
    qibuild_action.add_test_project("hellojavajni")
    hellojava = qibuild_action.add_test_project("hellojava")
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")
    jar.jar("hellojavajni.jar", ["hellojavajni"])
    deploy.deploy("com.test", "1.0-SNAPSHOT", "hellojavajni", "hellojavajni.jar", "file:///tmp/maven/")

    assert package.package(hellojava) == 0

    path = hellojava.path
    built_jar = os.path.join(path, "target/hellojava-1.0-SNAPSHOT.jar")
    assert os.path.exists(built_jar)
