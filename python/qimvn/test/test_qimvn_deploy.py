import pytest
import os
import qibuild.parsers

from qibuild.test.conftest import QiBuildAction
from qitoolchain.test.conftest import QiToolchainAction
from qimvn import deploy
from qimvn import jar
from qisys.command import CommandFailedException

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

def test_deploy(qibuild_action, local_repository):
    """ Test if directory where jar must be deployed exists.
    """
    qibuild_action.add_test_project("hellojavajni")
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")

    jarname = "test.jar"
    jarpath = jar.jar(jarname, ["hellojavajni"], get_paths())
    assert jarpath

    deploy_path = local_repository.replace("file://", "")
    artifactId = "hellojavajni"
    ver = "1.0"
    assert deploy.deploy("com.test", ver, artifactId, jarname, local_repository) == 0
    deploy_path = os.path.join(deploy_path, "com/test")
    deploy_path = os.path.join(deploy_path, artifactId)
    deploy_path = os.path.join(deploy_path, ver)
    deployed_jar = os.path.join(deploy_path, artifactId + "-" + ver + ".jar")
    assert os.path.exists(deployed_jar)

def test_failing_deploy(qibuild_action, local_repository):
    """ Test exceptions.
    """
    qibuild_action.add_test_project("hellojavajni")
    qibuild_action("configure", "hellojavajni")
    qibuild_action("make", "hellojavajni")

    jarname = "test.jar"
    jarpath = jar.jar(jarname, ["hellojavajni"], get_paths())
    assert jarpath

    deploy_path = local_repository.replace("file://", "")
    artifactId = "hellojavajni"
    ver = "1.0"
    #pylint: disable-msg
    with pytest.raises(CommandFailedException) as e:
        deploy.deploy("", ver, artifactId, jarname, local_repository)
    assert e.value.returncode == 1

    with pytest.raises(CommandFailedException) as e:
        deploy.deploy("com.test", ver, "", jarname, local_repository)
    assert e.value.returncode == 1

    with pytest.raises(CommandFailedException) as e:
        deploy.deploy("com.test", ver, artifactId, jarname, deploy_path)
    assert e.value.returncode == 1
