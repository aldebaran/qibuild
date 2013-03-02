import qisys.script
import qisys.sh

import pytest

def test_in_new_directory(tmpdir, git_server):
    git_server.create_repo("foo.git")
    git_server.create_repo("bar.git")

    with qisys.sh.change_cwd(tmpdir.strpath):
        qisys.script.run_action("qisrc.actions.init", [git_server.manifest_url])

def test_no_manifest(tmpdir):
    with qisys.sh.change_cwd(tmpdir.strpath):
        qisys.script.run_action("qisrc.actions.init")

def test_fails_when_not_empty(tmpdir):
    tmpdir.mkdir(".qi")
    with qisys.sh.change_cwd(tmpdir.strpath):
        # pylint: disable-msg=E1101
        with pytest.raises(Exception) as e:
            qisys.script.run_action("qisrc.actions.init")
        assert "empty directory" in e.value.message
