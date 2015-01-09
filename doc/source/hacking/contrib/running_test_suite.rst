.. _qibuild-test-suite:

Running qiBuild test suite
==========================


All in one step
---------------

Create a virtualenv to run your tests:

.. code-block:: console

  virtualenv venv
  source venv/bin/activate

Install qibuild with the "--editable" option, so that your
changes are reflected without the need to call ``pip install`` again

.. code-block:: console

  cd /path/to/qibuild
  pip install --editable .

Install all the test dependencies:

.. code-block:: console

    cd /path/to/qibuild/python
    pip install -r requirements.txt

Finally, run ``make``:

.. code-block:: console

  cd /path/to/qibuild/python
  make

This will use ``pylint`` to check for obvious errors, then run the full test suite.

Sometimes ``pylint`` is mistaken, you can fix this by adding a small comment
to disable the check, using the ``pylint`` error code:

.. code-block:: python

    # pylint: disable-msg=E1101

Running the test suite
----------------------

This is on a build farm but only for linux and python2.7, so it is possible
that some tests will fail.

If you do find a failing test, please open a bug.

If you find a bug, a nice way to make it easier to fix it is to write a
failing test and mark it as 'skipped'

.. code-block:: python

  @pytest.skip("See bug # ....")
  def test_subtle_bug(self):
     res = do_something_complicated()
     # Should be 42 but for some reason is 41 ...
     self.assertTrue(res, 42)


This way when the bug is fixed we just have to remove the ``@pytest.skip``
and we are sure the bug never occurs again.


Running only some tests
+++++++++++++++++++++++

You can use ``py.test`` like this:

  * Just for a given python package:

  .. code-block:: console

      cd python
      py.test qisrc

  * Just for a given test file:

  .. code-block:: console

     py.test qisrc/test/test_git.py

  * Just for a given test name:

  .. code-block:: console

     py.test qisrc/test/test_git.py -k set_tracking_branch

Note about debuggers
++++++++++++++++++++


If you are using ``ipdb`` or ``pdb`` to insert break points in the code like this:

.. code-block:: python

    # in foo.py
    def test_my_complicated_function():
        from IPython.core.debugger import Tracer; debug_here=Tracer()
        debug_here()


You will get an error message when you run ``py.test``

The solution is to use the ``-s`` option of ``py.test``:

.. code-block:: console

  $ py.test foo.py -s
