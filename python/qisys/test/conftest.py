## Copyright (c) 2012-2016 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import os
import re
import sys
import tempfile

import py
import pytest
import mock

from qisys import ui
import qisys.error
import qisys.sh
import qisys.script
import qisys.interact
import qisys.worktree

class TestNamespace(object):
    """ A class that behaves like a argparse.Namespace
    objects, except all unknown attributes are set to None

    """
    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError()
        setattr(self, name, None)
        return None

class TestWorkTree(qisys.worktree.WorkTree):
    """ A subclass of qisys.worktree.WorkTree that
    can create projects

    """
    def __init__(self, root=None):
        if root is None:
            # TestWorkTree is often used with cd_to_tmpdir fixture,
            # so this is safe
            self.root = os.getcwd()
        else:
            self.root = root
        super(TestWorkTree, self).__init__(self.root)

    @property
    def tmpdir(self):
        # pylint: disable-msg=E1101
        return py.path.local(self.root)

    def create_project(self, src):
        """ Create a new project """
        to_make = os.path.join(self.root, src)
        qisys.sh.mkdir(to_make, recursive=True)
        new_project = super(TestWorkTree, self).add_project(src)
        qiproject_xml = self.tmpdir.join(src, "qiproject.xml")
        qiproject_xml.write("""
<project format="3" />
""")
        return new_project

# Because sometimes the most popular OS in the world is not the best one ...
# pylint: disable-msg=E1101
skip_on_win = pytest.mark.skipif(os.name == 'nt', reason="cannot pass on windows")

def check_deploy_ssh():
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

# pylint: disable-msg=E1101
@pytest.fixture
def local_url(tmpdir):
    username = os.environ.get("LOGNAME")
    url = "%s@localhost:%s" % (username, tmpdir.strpath)
    return url

# pylint: disable-msg=E1101
skip_deploy = pytest.mark.skipif(not check_deploy_ssh(),
                                 reason="Cannot deploy with ssh")


# pylint: disable-msg=E1101
only_linux = pytest.mark.skipif(not sys.platform.startswith("linux"),
                                reason="only works on linux")

# pylint: disable-msg=E1101
@pytest.fixture
def worktree(cd_to_tmpdir):
    """ A new worktree in a temporary dir.
    As a bonus, we also change working dir to the temporary dir.
    This object has the same methods as WorkTree, plus:
        * worktree.tmpdir  : get the tmpdir as a py.LocalPath object
        * worktree.create_project : to create projects on the fly
    """
    wt = TestWorkTree()
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
    """ Configure qisys.ui to record the messages sent to the user """
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

    def find(self, pattern):
        regexp = re.compile(pattern)
        for message in ui._MESSAGES:
            if re.search(regexp, message):
                return message

@pytest.fixture(autouse=True)
def tmpfiles(request, tmpdir):
    """ Configure qisys.sh.get_*_path functions to return temporary
    files instead
    """
    # /tmp is a symlink on mac, leading to all kind of "interesting"
    # problems
    tmpdir = tmpdir.realpath()
    def fake_get_path(*args):
        prefix = args[0]
        rest = args[1:]
        full_path = os.path.join(tmpdir.strpath,
                                 os.path.basename(prefix),
                                 *rest)
        to_make = os.path.dirname(full_path)
        qisys.sh.mkdir(to_make, recursive=True)
        return full_path
    patcher = mock.patch("qisys.sh.get_path", fake_get_path)
    patcher.start()
    request.addfinalizer(patcher.stop)

@pytest.fixture
def cd_to_tmpdir(monkeypatch, tmpdir):
    workdir = tmpdir.mkdir("work")
    monkeypatch.chdir(workdir)
    return workdir

class TestAction(object):
    """ Helper class to test actions
    Make sure cwd is in a temporary directory,
    and provide a nicer syntax for qisys.script.run_action
    """
    def __init__(self, package):
        self.package = package
        self.worktree = TestWorkTree()

    def chdir(self, directory):
        try:
            directory = directory.strpath
        except AttributeError:
            pass
        os.chdir(directory)

    def __call__(self, action, *args, **kwargs):
        module_name = "%s.%s" % (self.package, action.replace("-", "_"))
        cwd = kwargs.get("cwd")
        if cwd:
            self.chdir(cwd)
        if kwargs.get("raises"):
        # pylint: disable-msg=E1101
            with pytest.raises(qisys.error.Error) as error:
                qisys.script.run_action(module_name, args)
            return str(error.value)
        if kwargs.get("retcode"):
            try:
                qisys.script.run_action(module_name, args)
            except SystemExit as e:
                return e.code
            return 0
        else:
            return qisys.script.run_action(module_name, args)

class QiSysAction(TestAction):
    def __init__(self):
        super(QiSysAction, self).__init__("qisys.actions")


# pylint: disable-msg=E1101
@pytest.fixture
def qisys_action(cd_to_tmpdir):
    return QiSysAction()
