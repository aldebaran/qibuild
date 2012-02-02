.. _qibuild-test-suite:

Running qiBuild test suite
==========================


Installing required packages
----------------------------

You need to install the following Python packages to run the test suite:

* python-nose
* python-mock

And you also need to install ``pylint``


Althought qiBuild is a cross-platform, running the test suite on Windows
with Visual Studio is quite painful. (Patches welcome ...)


All in one step (Unix only)
----------------------------

Simply go to ``qibuild/python`` and run ``make``

Note: if you are on a distribution where ``/usr/bin/python`` is Python3,
you should use

.. code-block:: console

    make PYTHON=python2


This will use pylint to find obvious errors (like variables referenced
before assignement, missing imports, and so on), then will run
the automatic tests.

Sometime pylint is mistaken, you can fix this by adding a small comment
to disable the check, using the pylint error code:

.. code-block:: python

    # pylint: disable-mgs=E1101

Check for pylint
----------------

Either run:

.. code-block:: console

    $ make check-all

Or run pylint with the ``pylint.rc`` you will find in ``qibuild/python``.

The score must NOT go below 9/10.



Running test suite
------------------

Use:

.. code-block:: console

   $ cd qibuild/python
   $ PYTHONPATH=. python run_tests.py


This is not yet on a build farm, so it is possible that some test will fail.

If you do find a failing test, please open a bug.

If you find a bug, a nice way to make it easier to fix it is to write a
failing test and mark it as 'skipped'

.. code-block:: python

  @unittest.skip("See bug # ....")
  def test_subtle_bug(self):
     res = do_something_complicated()
     # Should be 42 but for some reason is 41 ...
     self.assertTrue(res, 42)


This way when the bug is fixed we just have to remove the ``@unittest.skip``
and we are sure the bug never occurs again.
