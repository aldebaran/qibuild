# Copyright (c) 2012-2018 SoftBank Robotics. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the COPYING file.

import os
import re

import py
import pytest
import mock

from qisys import ui
import qisys.sh
import qisys.script
import qisys.interact
import qisys.worktree

# pylint: disable=redefined-outer-name


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

    __test__ = False  # Tell PyTest to ignore this Test* named class: This is as test to collect

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
<project version="3" />
""")
        return new_project


# Because sometimes the most popular OS in the world is not the best one ...
# pylint: disable-msg=E1101
skip_on_win = pytest.mark.skipif(os.name == 'nt', reason="cannot pass on windows")

# pylint: disable-msg=E1101


@pytest.fixture
def worktree(cd_to_tmpdir):  # pylint: disable=unused-argument
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
def args(request):  # pylint: disable=unused-argument
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


class MessageRecorder(object):
    def __init__(self):
        ui.CONFIG["record"] = True
        ui._MESSAGES = list()  # pylint: disable=protected-access

    @staticmethod
    def stop():
        ui.CONFIG["record"] = False
        ui._MESSAGES = list()  # pylint: disable=protected-access

    @staticmethod
    def reset():
        ui._MESSAGES = list()  # pylint: disable=protected-access

    @staticmethod
    def find(pattern):
        regexp = re.compile(pattern)
        for message in ui._MESSAGES:  # pylint: disable=protected-access
            if re.search(regexp, message):
                return message


@pytest.fixture(autouse=True)
def tmpfiles(request, tmpdir):
    """ Configure qisys.sh.get_*_path functions to return temporary
    files instead
    """

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

    @staticmethod
    def chdir(directory):
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
            with pytest.raises(Exception) as error:
                qisys.script.run_action(module_name, args)
            return str(error.value)
        if kwargs.get("retcode"):
            try:
                qisys.script.run_action(module_name, args)
            except SystemExit as e:
                return e.code
            return 0

        return qisys.script.run_action(module_name, args)
