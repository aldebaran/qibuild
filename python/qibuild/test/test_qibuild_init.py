""" test qibuild init """
import qisys.script
import pytest


def test_works_from_an_empty_dir(tmpdir, monkeypatch):
    ''' positive test '''
    monkeypatch.chdir(tmpdir)
    qisys.script.run_action("qibuild.actions.init")
    assert tmpdir.join(".qi").check(dir=True)


def test_fails_if_qi_dir(tmpdir, monkeypatch):
    ''' negative test '''
    tmpdir.mkdir(".qi")
    monkeypatch.chdir(tmpdir)
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as err:
        qisys.script.run_action("qibuild.actions.init")
    assert ".qi directory" in str(err.value)
