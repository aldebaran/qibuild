qisrc.test.fake_git
====================

.. py:module:: qisrc.test.fake_git

FakeGit
-------

.. autoclass:: FakeGit

  .. automethod:: FakeGit.add_result

  .. automethod:: FakeGit.check


The class has exactly the same methods as :py:mod:`qisrc.git.Git`,
but everything happens in memory. The filesystem is never touched,
no command is actually run.

It is used for testing :py:mod:`qisrc.git` functions.

The test should be written in 3 steps:

* Specify what will happen: for every git command, call
  :py:meth:`add_result` with what will be the retcode
  and the output
* Perform some tests
* Check that every expected git command has run

For instance

.. code-block:: python

    git = FakeGit("src")
    git.add_result("fetch", 0, "")

    # ... do something with the git object

    # Make sure that git.fetch() has been called exactly once
    git.check()


The idea is that you can test how `qisrc` would behave in extreme
corner cases without having to do complex set ups.

For instance, while on the 'master' branch,
``git checkout -f next`` can fail even if the
'next' branch exists because there are more files in ``next`` and
we will get a 'no space left on device' error.

Testing that is as easy as:

.. code-block:: python

    git = FakeGit("src")
    git.add_result("checkout", 2, "No space left on device")
