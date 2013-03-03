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
    recorder = MessageRecorder()
    request.addfinalizer(recorder.stop)
    return recorder

class MessageRecorder():
    def __init__(self):
        ui.CONFIG["record"] = True
        ui._MESSAGES = list()

    def stop(self):
        ui.CONFIG["record"] = False
        ui._MESSAGES = list()

    def reset(self):
        ui._MESSAGES = list()


class TestAction(object):
    """ Helper class to test actions
    Make sure cwd is in a temporary directory,
    and provide a nicer syntax for qisys.script.run_action
    """
    def __init__(self, package):
        self.tmp = tempfile.mkdtemp(prefix="tmp-test-qisrc-")
        self.old_cwd = os.getcwd()
        self.chdir(self.tmp)
        self.package = package

    def chdir(self, directory):
        try:
            directory = directory.strpath
        except AttributeError:
            pass
        os.chdir(directory)

    def __call__(self, action, *args, **kwargs):
        module_name = "%s.%s" % (self.package, action)
        cwd = kwargs.get("cwd")
        if cwd:
            self.chdir(cwd)
        if kwargs.get("raises"):
        # pylint: disable-msg=E1101
            with pytest.raises(Exception) as error:
                qisys.script.run_action(module_name, args)
            return error.value.message
        else:
            qisys.script.run_action(module_name, args)

    def reset(self):
        os.chdir(self.old_cwd)
        qisys.sh.rm(self.tmp)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.tmp)

    @property
    def worktree(self):
        return TestWorkTree(self.tmp)
