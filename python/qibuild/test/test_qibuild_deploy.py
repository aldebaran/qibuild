import qisys.command

def test_deploying_to_localhost(qibuild_action, tmpdir):
    # assume we can log in to localhost, and that
    # rsync and ssh are installed
    ssh = qisys.command.find_program("ssh")
    if not ssh:
        return

    rsync = qisys.command.find_program("rsync")
    if not rsync:
        return

    retcode = qisys.command.call(["ssh", "localhost", "date"], ignore_ret_code=True)
    if retcode != 0:
        return

    url = "localhost:%s" % tmpdir.strpath

    qibuild_action.add_test_project("world")
    qibuild_action.add_test_project("hello")
    qibuild_action("configure", "hello")
    qibuild_action("make", "hello")
    qibuild_action("deploy", "hello", url)
