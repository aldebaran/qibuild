Contributing to qibuild
=======================

Introduction
-------------

As usual contribution should take the form of "pull requests", like
most of github projects. But keep reading below for a list of
particularities.

Base your work on 'next' branch
-------------------------------

'master' branch is reserved for bug fixes and maintenance releases.
Development occurs on 'next' branch.

Test your pull request before submitting it
-------------------------------------------

Before submitting your pull request, you should check that the tests still pass,
and that ``pylint`` finds no errors

To do so:

* Create a ``virtualenv`` (see `virtualenv documentation
  <https://virtualenv.pypa.io/en/latest/userguide.html>`_ for details)

.. code-block:: console

   virtualenv ~/.venvs/qibuild
   source ~/.venvs/qibuild/bin/activate

* Install dependencies in the ``virtualenv``:

.. code-block:: console

    pip install -r requirements.txt
    pip install -e .

* Run ``pylint`` to check for errors:

.. code-block:: console

    pylint --errors-only /path/to/file.py

* Run the whole test suite:

.. code-block:: console

    cd python
    py.test -n NUM_CPUS


Make sure to update the changelog
---------------------------------

If one of your commits introduces a change in qibuild's behavior, you should
document it in the changelog. (In ``doc/source/changes/<version>.rst``)

You can do that in a separate commit or in the same commit that introduces the change.
