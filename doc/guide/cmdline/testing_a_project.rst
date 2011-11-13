.. _qibuild-testing-project:

Testing a project
=================

CMake comes with a testing tool called CTest.

The idea of CTtest is that you specify a executable to run, CTest launches the
executable, and the test passes if the return code is 0.

Assuming you have added some tests in your project, you can test them by
running:

.. code-block:: console

  $ qibuild test foo

In our case, this is simply going to launch the foo executable.

