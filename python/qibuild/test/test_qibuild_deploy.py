import os

import qisys.command

def check_ssh_connection():
    # check we can log in to locahost, and that
    # rsync and ssh are installed.
    ssh = qisys.command.find_program("ssh")
    if not ssh:
        return False

    rsync = qisys.command.find_program("rsync")
    if not rsync:
        return False

    retcode = qisys.command.call(["ssh", "localhost", "date"], ignore_ret_code=True)
    if retcode != 0:
        return False

    return True


def test_deploying_to_localhost(qibuild_action, tmpdir):
    # Nomical case : deploy to a single deploy directory.
    if not check_ssh_connection():
        return

    url = "%s@localhost:%s" % (os.getlogin(), tmpdir.strpath)

    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("deploy", "hello", url)

    assert tmpdir.join("lib").check(dir=True)
    assert tmpdir.join("bin").check(dir=True)


def test_deploying_to_several_urls(qibuild_action, tmpdir):
    # Deploy to several directories.
    if not check_ssh_connection():
        return

    url = "%s@localhost:%s" % (os.getlogin(), tmpdir.strpath)
    first_url = "%s/first" % url
    second_url = "%s/second" % url

    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("deploy", "hello", first_url, "--url", second_url)

    assert tmpdir.join("first").join("lib").check(dir=True)
    assert tmpdir.join("first").join("bin").check(dir=True)
    assert tmpdir.join("second").join("lib").check(dir=True)
    assert tmpdir.join("second").join("bin").check(dir=True)
