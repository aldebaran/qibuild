.. _qibuild-testing-project:

Testing a project
=================

You can add tests to your projects using the :cmake:function:`qi_add_test` functions.

You can then run the tests with:

.. code-block:: console

  $ qitest run foo



.. _qibuild-ctest:

Note for CTest users
---------------------

``qitest run`` does *not* use ``ctest`` executable, and ``qi_add_test`` is
*not* calling upstream ``add_test`` function.

The reasons for this are:

* ``qitest run`` is able to run any test executable, not just those coming
  from a ``CMake`` project. You can for instance run Python tests with
  ``qitest run`` by using ``qitest collect`` on Python projects.
  In fact,  you can run tests written in any language provided you can
  write or generate a ``qitest.json`` file.

.. todo:: add link to qitest doc

* We need to be able to run the tests after they have been deployed, and
  ``CTest`` does not support this use case
* Having a test runner implemented in Python made it possible for us to implement
  more features such as running tests with ``valgrind``, or specify a CPU mask
  for each test.

This means that you cannot use ``set_test_properties`` for a test created
with ``qi_add_test``

Also note that ``qitest run`` is intended to be used with `Jenkins <http://jenkins-ci.org/>`_, instead of ``CDash``.

qitest run features
-------------------


* ``qitest run`` will always generate JUnit-like XML files for each test
  (in ``project/<build-dir>/sdk/test-resuls/<testname>.xml``), so you do not
  have to use any test framework to generate the XML for you.

* The tests are run from ``<build>/sdk/bin`` by default, which is handy on
  Windows to make sure executables can find the ``dlls`` they depend on.

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
  file behind. But ``qitet run`` will handle this case nicely, producing a
  nice XML Junit files with an error message about the time out or the segfault.

.. code-block:: xml

   <testsuite name="test">
    <testcase name="test_foo" status="run">
      <failure message="Timed out (2 s)">
      </failure>
    </testcase>
  </testsuite>

* You can run your tests with valgrind using ``qitest run --valgrind``. It will
  check for memory and file descriptors leaks and make the test fail if some
  are detected

* You can generate XML and HTML coverage reports by:
  * Running ``qibuild configure`` with the ``-coverage`` option
  * Installing ``gcovr``
  * Run ``qitest run --coverage``
