.. _cmake-test:

Unit testing
============

Here we will just add a test that checks that
forty plus two are forty-two. (Just in case ...)

Adding a test
--------------

Call :cmake:function:`qi_create_test` with the first argument being the name of
the test, and the rest being the sources of the executable.

.. code-block:: cmake

  qi_create_test(foo_test test.cpp)

If you have arguments to pass to the executable you want to test,
simply add them to the :cmake:function:`qi_create_test` call, like this:

.. code-block:: cmake

    qi_create_test(foo_test foo_test.cpp ARGUMENTS "--foo=bar")


If you have ``gtest`` installed, you can use
:cmake:function:`qi_create_gtest`:

.. code-block:: cmake

    qi_create_gtest(foo_test foo_test.cpp
      DEPENDS gtest)

This will automatically add the `--xml-output` option
to store the results of the test as XML files in
``foo/<build-dir>/sdk/tests-results``, which is useful when
you are doing continuous integration.

If you need to run the same executable with different
arguments, you should use a lower-level function
called :cmake:function:`qi_add_test`

.. code-block:: cmake

   qi_create_test_helper(test_launcher
    test_launcher.cpp)

   qi_add_test(test_launch_foo
    test_launcher
      ARGUMENTS "foo")

   qi_add_test(test_launch_bar
    test_launcher
      ARGUMENTS "bar")

Note how we call ``qi_create_test_helper`` instead of
``qi_create_bin`` in order to make sure the test executable
does not get installed by default.

Running the tests
-----------------

To run the tests, configure and build the project, then
use ``qitest run``:

.. code-block:: console

    qibuild configure
    qibuild make
    qitest run


Important
---------

Please read :ref:`qibuild-ctest` before using ``qitest run``
for continuous integration.
