qibuild.test_runner -- Running tests from a C++ project
========================================================

.. automodule:: qibuild.test_runner

ProjectTestRunner
-----------------

.. autoclass:: ProjectTestRunner
    :members:

    .. py:attribute:: perf

      Whether we should run performance tests

    .. py:attribute:: nightly

      Whether we should run nightly tests

    .. py:attribute:: nightmare

      Sets ``GTEST_REPEAT=20`` and ``GTEST_SHUFFLE=1``

    .. py:attribute:: valgrind

      Run with valgrind and make the tests fail if there are
      memory leaks or file descriptor leaks

    .. py:attribute:: num_cpus

      Assigns the given number of CPUS for each test. Useful
      to trigger race conditions.
      For instance, with a machine with 8 CPUs you could run

      .. code-block:: console

        qitest run --ncpu=2 -j4

ProcessTestLauncher
-------------------

.. autoclass:: ProcessTestLauncher
   :members:

   .. py:attribute: test_out

      Where to find the Junit XML files

   .. py:attribute: perf_out

      Where to find the XML results of the performance tests
