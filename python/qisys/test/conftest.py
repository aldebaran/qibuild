import argparse
import os
import tempfile

import py
import pytest
import mock

from qisys import ui
import qisys.sh
import qisys.interact
import qisys.worktree

class TestNamespace(object):
    """ A class that behaves like a argparse.Namespace
    objects, except all unknown attributes are set to None

    """
    def __getattr__(self, name):
        setattr(self, name, None)
        return None

class TestWorkTree(qisys.worktree.WorkTree):
    """ A subclass of qisys.worktree.WorkTree that
    can create projects

    """
    def __init__(self, root):
        super(TestWorkTree, self).__init__(root)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.root)

    def create_project(self, src):
        """ Create a new project """
        to_make = os.path.join(self.root, src)
        qisys.sh.mkdir(to_make, recursive=True)
        new_project = super(TestWorkTree, self).add_project(src)
        return new_project

# pylint: disable-msg=E1101
@pytest.fixture
def worktree(request):
    """ A new worktree in a temporary dir.
    This object has the same methods as WorkTree, plus:
        * worktree.tmpdir  : get the tmpdir as a py.LocalPath object
        * worktree.create_project : to create projects on the fly
    """
    tmp = tempfile.mkdtemp(prefix="tmp-test-worktree")
    def clean():
        qisys.sh.rm(tmp)
    request.addfinalizer(clean)
    wt = TestWorkTree(tmp)
    return wt

# pylint: disable-msg=E1101
@pytest.fixture
def interact(request):
    """ Replace all functions in qisys.interact, and
    let the user predifine the answers, and inspect the
    questions that were asked

    """
    from qisys.test.fake_interact import FakeInteract
    fake_interact = FakeInteract()
    patcher = mock.patch('qisys.interact', fake_interact)
    request.addfinalizer(patcher.stop)
    return patcher.start()

@pytest.fixture
def args(request):
    """ Forge argparse.Namespace objects
    All unknown attributes will be initialized to
    None

    """
    return TestNamespace()



@pytest.fixture
def record_messages(request):
    """ Configure qisys.ui to record the messges sent to the user """
    ui.CONFIG["record"] = True
    ui._MESSAGES = list()
    def reset():
        ui.CONFIG["record"] = False
        ui._MESSAGES = list()
    request.addfinalizer(reset)
