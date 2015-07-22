.. _qipy-tutorial:

Using Python with qibuild projects
===================================


Introduction
------------


Let's say you have a C++ library in a qibuild project, called ``foo``.

.. code-block:: console

    <worktree>
    |__ foo
        |__ qiproject.xml
        |__ CMakeLists.txt
        |__ foo.cpp
        |__ foo.hpp

.. code-block:: cmake

    # in <worktree>/foo/CMakeLists.txt
    project(foo)
    find_package(qibuild)

    qi_create_lib(SHARED foo foo.hpp foo.cpp)

.. code-block:: xml

    <!-- in <worktree>/foo/qiproject.xml -->
    <project version="3">
      <qibuild name="foo" />
    </project>

You wish to write a C++ Python extension in another project to wrap the
``foo`` library, using the qibuild build system. Let's say you use swig for
this.

You have an interface file for swig called ``pyfoo.i`` which is going
to generate a ``_pyfoo.so`` Python extension, and a ``foo.py`` to wrap
the C++ extension.

.. code-block:: console

    <worktree>
    |__ foo
        |__ qiproject.xml
        |__ CMakeLists.txt
        |__ foo.cpp
        |__ foo.hpp
    |__ pyfoo
        |__ qiproject.xml
        |__ CMakeLists.txt
        |__ pyfoo.i
        |__ foo.py
        |__ foo_script.py

.. code-block:: xml

    <!-- in pyfoo/qiproject.xml -->
    <project version="3">
      <qibuild name="pyfoo">
        <depends runtime="true" buildtime="true" names="foo" />
      </qibuild>
      <qipython name="pyfoo">
        <setup with_distutils="true" />
      </qipython>
    </project>

.. code-block:: cmake

    # in <worktree>/foo-py/CMakeLists.txt
    project(pyfoo)

    qi_swig_python(_pyfoo pyfoo.i DEPENDS FOO)

.. code-block:: cpp

    // In pyfoo.i
    %module _pyfoo

    %{
    #include "foo.hpp"
    %}

    %include "foo.hpp"

.. code-block:: py

    # In foo.py

    import _pyfoo

    ...

    # In foo_script.py
    import foo

    ...

    def main():
        ....

    if __name__ == "__main__":
        main()


You want to be able to build the ``pyfoo`` extension, and use ``foo-script.py``
directly without having to set ``PYTHONPATH`` to something like:
``<worktree>/pyfoo/build-linux64/sdk/lib``.

In order to do so, you can write a ``setup.py`` for your python project
(``pyfoo``, and use ``qipy`` to run the script)

Under the cover, everything will be done using a ``virtualenv`` and ``distutils``.

Some useful links:

* `Swig <http://www.swig.org/>`_

* `virtualenv <https://virtualenv.pypa.io/en/latest/>`_

* `Writing a setup.py file <https://docs.python.org/2/distutils/index.html>`_


Step one: Basic checks
----------------------

Just make sure your project is listed when running ``qipy list``,
and that the extension is built:

.. code-block:: console

    qibuild configure pyfoo
    qibuild make pyfoo


Step two: Write a setup.py file
-------------------------------

.. code-block:: python


    # in pyfoo/setup.py
    import os
    from setuptools import setup

    setup(name="mymodule",
          version="0.1",
          py_modules=['foo'],
          entry_points = {
             "console_scripts" : [
               "pyfoo = foo_script:main"
              ]
          }
    )

Step three: Use `qipy bootstrap`
--------------------------------

.. code-block:: console

    qipy bootstrap

This will initialize a virtualenv in the worktree, and should be run
when changing or adding new python projects.

You can use a ``-c`` option to have several virtualenv in the worktree.

The virtualenv will be initialized using ``pip install --editable``, so you
will be able to run your python code directly from the sources.

Also, the ``qi_swig_python`` CMake call will add the path to the extension library
in a ``qi.pth`` file in the virtualenv.

Step four: Use the virtualenv
-----------------------------

Just use ``qipy run`` instead of ``python``

``qipy run [-c config] foo_script.py``

If you have several commands to run, use something like
``source $(qipy sourceme -q)`` to activate the virtualenv in your
current session.


Step five: adding Python tests
------------------------------

It's recommended to use `pytest <http://pytest.org/latest/>`_ to run your
tests.

You can do something like

.. code-block:: console

    cd /path/to/project
    qipy run -- py.test -- [OTHER py.test args]

If you get a segmentation fault while running your tests
(which can happen when you write C++ Python extensions),
here is how to run ``pytest`` inside ``gdb``:

.. code-block:: console

    source $(qipy sourceme -q)
    gdb /path/to/worktree/.qi/venv/py-<config>/bin/python
    run -m pytest
