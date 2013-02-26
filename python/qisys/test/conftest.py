import tempfile

import pytest
import mock

import qisys.sh
import qisys.interact
import qisys.worktree

# pylint: disable-msg=E1101
@pytest.fixture
def worktree(request):
    tmp = tempfile.mkdtemp(prefix="tmp-test-worktree")
    def clean():
        qisys.sh.rm(tmp)
    request.addfinalizer(clean)
    wt = qisys.worktree.create(tmp)
    return wt

# pylint: disable-msg=E1101
@pytest.fixture
def interact(request):
    from qisys.test.fake_interact import FakeInteract
    fake_interact = FakeInteract()
    patcher = mock.patch('qisys.interact', fake_interact)
    request.addfinalizer(patcher.stop)
    return patcher.start()
