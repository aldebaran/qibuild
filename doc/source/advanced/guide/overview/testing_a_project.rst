.. _qibuild-testing-project:

Testing a project
=================

You can add tests to your projects using the :cmake:function:`qi_add_test` functions.

You can then run the tests with:

.. code-block:: console

  $ qibuild test foo



.. _qibuild-ctest:

Note for CTest users
---------------------

``qibuild test`` does *not* use ``ctest`` executable, and ``qi_add_test`` is
*not* calling upstream ``add_test`` function.

The reasons for this are:

* ``qibuild test`` is just actually calling ``qitest run`` which is able to
  run any test executable, not just those coming from a ``CMake`` project.
* we needed to be able to run the tests after they have been deployed, and
  ``CTest`` does not support this use case
* Having a test runner implemented in Python made it possible for us to implement
  more features such as running tests with ``valgrind``, or specify a CPU mask
  for each test.

This means that you cannot use ``set_test_properties`` for a test created
with ``qi_add_test``

Also note that ``qibuild test`` is intended to be used with `Jenkins <http://jenkins-ci.org/>`_, instead of ``CDash``.

qibuild test features
---------------------


* ``qibuild test`` will always generate JUnit-like XML files to
  ``project/build-tests/results``, so you do not have to use any test framework
  to generate the XML for you.

* The tests are run from ``<build>/sdk/bin`` by default.

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
  file behind. But ``qibuild test`` will handle this case nicely, producing a
  nice XML Junit files with an error message about the time out or the segfault.

.. code-block:: xml

   <testsuite name="test">
    <testcase name="test_foo" status="run">
      <failure message="Timed out (2 s)">
      </failure>
    </testcase>
  </testsuite>


