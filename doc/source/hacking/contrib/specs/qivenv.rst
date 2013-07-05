qivenv: virtualenv meets worktree
==================================

General
--------

Main goal: make it easy to work with Python code inside a worktree,
i.e avoid having to manually set ``PYTHONPATH`` and other environment
variables.


We'll use ``pip`` and ``virtualenv`` because they are becoming
the standard to deal with this kind of issues.

More precisely:

* Handle 3rd-party libraries

* Handle code that is inside a worktree, which means it's possible
   to use 'import foo' and directly use the code from ``<worktree>/foo``,
   without having to write a ``setup.py``

* Handle python extensions written in C++ depending one one or more
  qibuild CMake projects.

* Handle C++ code that embeds a Python interpreter and loads Python extensions.


3rd party libraries
--------------------

This is useful for instance in ``qidoc``, to specify  the ``sphinx`` version and its deps,
or the tools in ``spinxcontrib``, and so on.

This is also useful for whatever ``Python`` project.

Solution
+++++++++

* A ``requirements.txt`` (as usual for pip)

* A hidden virtualenv in ``.qi/venv`` automatically created and activated.

For instance, for ``qidoc``, we read the ``requirements.txt`` from the templates repo
if it exists and use a virtualenv in ``.qi/venv/qidoc``


Python code inside worktree
----------------------------

* We'll keep the ``qiproject.xml`` syntax

.. code-block:: xml

    <qiproject version="3">
      <pyproject name="foo" />
    </qiproject>

* By default, name is read from ``setup.py`` if it exists

* By default, list of deps is read from ``requirements.txt`` if it exists

* The virtualenv is in <worktree>/.qi/venv/<name>
  The tool automatically add the paths of the python projects to
  <worktree>.qi/venv/<name>/lib/site-packages/qivenv.pth


Python that depends on C++
---------------------------

* Exactly the same thing, except that we add ``<build>/sdk/lib/python<version>/site-pacakges>`` to the ``.pth`` file

* We also do the required magic in CMake so that setting ``PATH``, ``LD_LIBRARY_PATH``
  or ``DYLD_LIBRARY_PATH`` is not necessary, OR we generate a python wrapper that does this.


Embedded Python interpreter in C++
-------------------------------------

Again, the same thing, but we use ``virtualenv --python=${PYTHON_EXECUTABLE}``, wher
PYTHON_EXECUTABLE is found by CMake. So if you are using Python from your system,
nothing changes, and if you are using Python from a toolchain, you use it in the
virtualenv.


Command line API
----------------

* ``qivenv list`` : list the available virtualenvs in the worktree
* ``qivenv add <name> [-c config]``: add a new virtualenv to the worktree
* ``qivenv rm <name>``: remove a virtualenv from the worktree
* ``qivenv use <name>``: use the given virtualenv


Examples:

Running py.test
+++++++++++++++

I want to run ``py.test`` on the ``foo`` project that depends on the ``bar`` project.

* In ``foo/requirements.txt`` I add:

::

    pytest

* Then I run

::

  $ qivenv use default


Using some Python extension that depends on C++ code
++++++++++++++++++++++++++++++++++++++++++++++++++++++

::

  $ qibuild configure -c <config> myext
  $ qivenv add <config>
  $ qivenv use <config>

  $ python
  >>> import myext
