.. _qitest-tutorial:

Running tests with qitest
=========================

The qitest.json file
---------------------

``qitest`` is an command line tool that is able to run tests defined in a
JSON file, usually called ``qitest.json``.

The format of the JSON file looks like this:

.. code-block:: json

    [
       { "name" : "test_one", "cmd" : ["/path/to/test_one"] },
       { "name" : "test_two", "cmd" : ["/path/to/test_two", "arg1", "arg2"] }
    ]

The tests are defined as a list of dictionaries.

Here there are two tests defined: ``test_one`` and ``test_two``

Each test should at least have a ``name`` and a command line (``cmd``)

``cmd`` is the command line that should be launched.

Additionally, ``qitest`` recognize the following keys in the dictionary:

* ``working_directory`` The directory where to run the command.
* ``nigthly`` A boolean indicating whether the test is a "nightly" test.
  Nightly tests are not run by default, to run them, use ``qitest run --nigtly``
* ``perf`` A boolean indicating whether the test is a performance test.
  Performance tests are not run by default, to run them, use ``qitest run --perf``
* ``gtest`` : A boolean indicating whether the test is using Google test framework.
  If true ``qitest run`` will add a correct ``--gtest_output`` option to the
  command line
* ``pytest`` : A boolean indicating whether the test is meant to run with ``py.test``.
  If true, ``qitest run`` will add a correct ``--junit-xml`` option to the command line.
* ``timeout`` : A duration in seconds. ``qitest run`` will mark the test as failed
  if the command line does not terminate before the specified duration.


Using qitest with qibuild C++ projects
--------------------------------------

If your project is a C++ qibuild project, you can use
:cmake:function:`qi_create_test` and friends to create your tests.
The ``qitest.json`` file will be created by ``qibuild make`` in the build directory
of your project.

To create performance or nightly tests, use :cmake:function:`qi_create_test` with
the keyword ``PERF`` or ``NIGHTLY``

To specify a timeout, use :cmake:function`qi_create_test` with a ``TIMEOUT`` argument.

``qitest run`` , when used from the root directory of a ``qibuild`` project
will try and find the ``qitest.json`` file in the build directory automatically.

Running deployed tests
----------------------

You can also run tests after having deployed your code to a remote target with
``qibuild deploy``.

To do so, assuming ``qitest`` is installed on the remote target, run:

.. code-block:: console

    qibuild deploy --with-tests --url user@host:deploy-dir
    ssh use@host
    cd deploy-dir
    qitest run


Using qitest with Python projects
----------------------------------

If your project is a Python project registered for ``qipy`` and the tests are
using ``py.test``, you can generate a ``.json`` file for ``qitest`` by running:

.. code-block:: console

    qitest collect

This will generate a ``pytest.json`` file for each Python project.

Then you can run ``qitest`` with:

.. code-block:: console

    qitest run --qitest-json pytest.json
