.. _cmake-test:

Unit testing
============

Here we will just add a test that checks that
forty plus two are forty-two. (Just in case ...)

Adding a test
--------------

You first need to call ``enable_testing()``

Then you call :cmake:function:`qi_create_test` with the first argument being the name of
the test, and the rest being the sources of the executable.

.. code-block:: cmake

  enable_testing()
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
``foo/build-tests/results``, which is useful when
you are doing continuous integration.

If you need to run the same executable with different
arguments, you should use a lower-level function
called :cmake:function:`qi_add_test`

.. code-block:: cmake

   qi_create_bin(test_launcher
    test_launcher.cpp NO_INSTALL)

   qi_add_test(test_launch_foo
    test_launcher
      ARGUMENTS "foo")

   qi_add_test(test_launch_bar
    test_launcher
      ARGUMENTS "bar")


Important
---------

Please read :ref:`qibuild-ctest` before using ``qibuild test``
for continuous integration.

