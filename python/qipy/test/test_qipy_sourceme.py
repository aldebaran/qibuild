import os

def test_simple(qipy_action):
    qipy_action("bootstrap")
    res = qipy_action("sourceme")
    assert os.path.exists(res)

def test_error_when_venv_does_not_exist(qipy_action):
    error = qipy_action("sourceme", raises=True)
    assert "does not exist" in error
