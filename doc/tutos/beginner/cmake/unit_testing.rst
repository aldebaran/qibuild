Unit testing
============

Here we will just add a test that tries to launch the foo executable that we
have just built.

This test is often called zero_test because the least thing you can expect for
your executable is that it runs without crashing.

Adding a test
--------------

You first need to call enable_testing()

Then you call add_test() with the first argument being the name of the test,
the second being the name of the exeuctable.

.. code-block:: cmake

  enable_testing()
  qi_add_test(zero_test foo)

.. note:: If you have arguments to pass to the executable you want to test,
   simply add them to the qi_add_test call.
