# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.
import os

import qisys.command
import qibuild.find

# pylint: disable=unused-variable


def check_ssh_connection():
    # check we can log in to locahost, and that
    # rsync and ssh are installed.
    ssh = qisys.command.find_program("ssh")
    if not ssh:
        return False

    rsync = qisys.command.find_program("rsync")
    if not rsync:
        return False

    retcode = qisys.command.call(["ssh", "localhost", "true"], ignore_ret_code=True)
    if retcode != 0:
        return False

    return True


def get_ssh_url(tmpdir):
    username = os.environ.get("LOGNAME")
    url = "%s@localhost:%s" % (username, tmpdir.strpath)
    return url


def test_deploying_to_localhost(qibuild_action, tmpdir):
    # Nomical case : deploy to a single deploy directory.
    if not check_ssh_connection():
        return

    url = get_ssh_url(tmpdir)

    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("deploy", "hello", "--url", url)

    assert tmpdir.join("lib").check(dir=True)
    assert tmpdir.join("bin").check(dir=True)


def test_deploying_to_several_urls(qibuild_action, tmpdir):
    # Deploy to several directories.
    if not check_ssh_connection():
        return
    url = get_ssh_url(tmpdir)
    first_url = "%s/first" % url
    second_url = "%s/second" % url

    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("deploy", "hello", "--url", first_url, "--url", second_url)

    assert tmpdir.join("first").join("lib").check(dir=True)
    assert tmpdir.join("first").join("bin").check(dir=True)
    assert tmpdir.join("second").join("lib").check(dir=True)
    assert tmpdir.join("second").join("bin").check(dir=True)


def test_deploying_tests(qibuild_action, tmpdir):
    if not check_ssh_connection():
        return
    url = get_ssh_url(tmpdir)
    qibuild_action.add_test_project("testme")
    qibuild_action("configure", "testme")
    qibuild_action("make", "testme")
    # default is no tests:
    qibuild_action("deploy", "testme", "--url", url)
    assert tmpdir.join("bin/ok").check(file=False)
    qibuild_action("deploy", "--with-tests", "testme", "--url", url)
    assert tmpdir.join("bin/ok").check(file=True)


def test_deploy_builds_build_deps(qibuild_action, tmpdir):
    if not check_ssh_connection():
        return
    url = get_ssh_url(tmpdir)
    foo_proj = qibuild_action.create_project("foo")
    bar_proj = qibuild_action.create_project("bar", build_depends=["foo"])
    qibuild_action("configure", "bar")
    qibuild_action("make", "bar")
    qibuild_action("deploy", "bar", "--url", url)
    qibuild.find.find([foo_proj.sdk_directory], "foo", expect_one=True)


def test_deploy_install_binary_packages(qibuild_action, qitoolchain_action,
                                        tmpdir):
    if not check_ssh_connection():
        return
    world = qibuild_action.add_test_project("world")
    hello = qibuild_action.add_test_project("hello")
    qitoolchain_action("create", "test")
    qibuild.config.add_build_config("test", toolchain="test")
    world_package = qibuild_action("package", "world")
    qitoolchain_action("add-package", "--config", "test", world_package)
    build_worktree = qibuild_action.build_worktree
    worktree = build_worktree.worktree
    worktree.remove_project("world", from_disk=True)
    qibuild_action("configure", "--config", "test", "hello")
    qibuild_action("make", "--config", "test", "hello")
    url = get_ssh_url(tmpdir)
    qibuild_action("deploy", "hello", "--config", "test", "--url", url)
