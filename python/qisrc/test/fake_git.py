## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

import pytest

import qisrc.git

class FakeGit(qisrc.git.Git):
    """ To be used as a mock object for testing

    """
    # Pseudo persistent config
    repo_configs = dict()

    def __init__(self, repo):
        self.repo = repo
        if not self.repo in FakeGit.repo_configs:
            FakeGit.repo_configs[repo] = dict()
        self.calls = list()
        self.calls_index = dict()
        self.results = dict()

    def get_config(self, name):
        return FakeGit.repo_configs[self.repo].get(name)

    def set_config(self, name, value):
        FakeGit.repo_configs[self.repo][name] = value

    def add_result(self, cmd, retcode, out):
        """ Add an expected result for the given command

        """
        if cmd in self.results:
            self.results[cmd].append((retcode, out))
        else:
            self.results[cmd] = [(retcode, out)]

    def get_result(self, cmd):
        """ Look for the expected result

        """
        if not cmd in self.results:
            raise Exception("Unexpected call to %s" % cmd)
        if not cmd in self.calls_index:
            self.calls_index[cmd] = 0
        index = self.calls_index[cmd]
        res_list = self.results[cmd]
        if index >= len(res_list):
            mess = "%s was called %s times " % (cmd, index+1)
            mess += "but only %s results were configured" % (len(res_list))
            raise Exception(mess)
        res = self.results[cmd][index]
        self.calls_index[cmd] += 1
        return res

    def check(self):
        """ Check that everything that was configured has been called """
        for (k, v) in self.results.iteritems():
            call_index = self.calls_index.get(k)
            if call_index is None:
                mess = "%s was added as result but never called" % k
                raise Exception(mess)
            if call_index != len(v):
                mess = "%s was configured to be called %s times " % (k, len(v))
                mess += "but was only called %s times" % (call_index)
                raise Exception(mess)


    def call(self, *args, **kwargs):
        """ Look for the return of the command in the list.
        If not found, assume it succeeds.

        """
        self.calls.append((args, kwargs))
        (retcode, out) = self.get_result(args[0])
        raises = kwargs.get("raises")
        if raises is False:
            return (retcode, out)
        else:
            if retcode != 0:
                raise Exception("%s failed" % args)


def test_persistent_config():
    git1 = FakeGit("repo")
    git1.set_config("foo.bar", 42)
    git2 = FakeGit("repo")
    assert git2.get_config("foo.bar") == 42
    assert git2.get_config("notset") is None


def test_fake_call():
    git = FakeGit("repo")
    git.add_result("fetch", 0, "")
    (retcode, _) = git.fetch(raises=False)
    assert retcode == 0
    git2 = FakeGit("repo2")
    git2.add_result("fetch", 2, "Remote end hung up unexpectedly")
    (retcode, out) = git2.fetch(raises=False)
    assert retcode == 2
    assert "Remote end hung up" in out

def test_wrong_setup():
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.checkout("-f", "master")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        git.fetch()
    assert "Unexpected call to fetch" in e.value.message

def test_configured_but_not_called_enough():
    git = FakeGit("repo")
    git.add_result("checkout", 0, "")
    git.add_result("checkout", 1, "Unstaged changes")
    git.checkout("next")
    # pylint: disable-msg=E1101
    with pytest.raises(Exception) as e:
        git.check()
    assert "checkout was configured to be called 2 times" in e.value.message
    assert "was only called 1 times" in e.value.message

def test_configured_but_not_called():
    git = FakeGit("repo")
    git.add_result("checkout", 1, "")
    git.add_result("reset", 0, "")
    # pylint: disable-msg=E1101
    git.checkout(raises=False)
    with pytest.raises(Exception) as e:
        git.check()
    assert "reset was added as result but never called" in e.value.message

def test_commands_are_logged():
    git = FakeGit("repo")
    git.add_result("fetch", 0, "")
    git.add_result("reset", 0, "")
    git.fetch()
    git.reset("--hard", quiet=True)
    calls = git.calls
    assert len(calls) == 2
    assert calls[0][0] == ("fetch",)
    assert calls[1][0] == ("reset", "--hard")
    assert calls[1][1] == {"quiet" : True}
