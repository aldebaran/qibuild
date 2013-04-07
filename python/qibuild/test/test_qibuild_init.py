import qisys.script

import pytest

def test_works_from_an_empty_dir(tmpdir, monkeypatch):
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qibuild.actions.init")
    assert tmpdir.join(".qi").check(dir=True)

def test_fails_from_an_non_empty_dir(tmpdir, monkeypatch):
    tmpdir.mkdir("foo")
    monkeypatch.chdir(tmpdir)
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        qisys.script.run_action("qibuild.actions.init")
    assert "empty directory" in str(e.value)
