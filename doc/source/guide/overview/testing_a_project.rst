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


Note that for this to work you nedd to have called
``enable_testing()``  and ``add_test`` (or :cmake:function:`qi_create_test`, or
:cmake:function:`qi_create_gtest`) somewhere in your ``CMakeLists.txt``


.. _qibuild-ctest:

Note for CTest users
---------------------

``qibuild test`` does NOT use ``ctest`` executable.

Instead, ``qibuild`` contains a ``ctest`` implementation in pure Python.

This means ``qibuild tests`` parses CMake generated code to know how
to run the tests, so not all features of ``set_test_properties`` are handled ...

Also, ``qibuild test`` is optimized to be used with `Jenkins <http://jenkins-ci.org/>`_,
**not** with upstream's ``CDash``.

Caveats
+++++++

If you are using ``add_test()`` directly, make sure
the second argument is **the full path** of the tests you are building

.. code-block:: cmake

     # Bad : `qibuild test` won't know where ``test_foo`` is:
     add_executable(test_foo test_foo.cpp)
     add_test(test_foo test_foo)

     # OK: we set the RUNTIME_OUTPUT_PROPERTIES and use it:
     set(_out "${CMAKE_CURRENT_BINARY_DIR}")
     add_executable(${name}  ${${name}_SRC})
     set_target_properties("${name}" PROPERTIES
         RUNTIME_OUTPUT_DIRECTORY         "${_out}"
     )
     add_test(${name} "${_out}/${name}")

     # OK: does the same as above but with just one line ;)
     qi_create_test(test_foo test_foo.cpp)


You should always call ``enable_testing()`` for ``qibuild test`` to work.
If you don't want to build any test, you should set ``BUILD_TESTS=OFF``.


qibuild test features
~~~~~~~~~~~~~~~~~~~~~

* `qibuild test` will always generate Junite-like XML files to
  ``project/build-tests/results``, so you do not have to use any test framework
  to generate the XML for you.

* If your test is a simple executable and you only care about the return code,
  the generated XML will contain the full output of the program and the return
  code.

.. code-block:: xml

  <testsuite name="test">
    <testcase name="test_foo" status="run">
      <failure message="Return code: 2">
        <![CDATA[
    ERROR: ...
        ]]>
      </failure>
    </testcase>
  </testsuite>

* If you use ``qi_create_gtest``, the test will be called with
  the correct ``--gtest-output`` function for you

* If your GTest test times out, or segfaults, it sometimes leaves an invalid XML
  find behind. But ``qibuild test`` will handle this case nicely, producing a
  nice XML Junit files with an error message about the time out or the segfault.

.. code-block:: xml

   <testsuite name="test">
    <testcase name="test_foo" status="run">
      <failure message="Timed out (2 s)">
      </failure>
    </testcase>
  </testsuite>


* The environment variables such as ``DYLD_LIBRARY_PATH`` or ``DYLD_FRAMEWORK_PATH``
  will be set for you.

* The tests will run from the main CMake build dir, instead of ``CMAKE_CURRENT_SOURCE_DIR``.
  So if ``qi_add_test`` is in ``src/foo/bar/CMakeLists.txt``, the working dir will be
  ``src/foo/build/`` instead of ``src/foo/build/bar``.
