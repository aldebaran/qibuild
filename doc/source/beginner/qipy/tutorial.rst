.. _qipy_tutorial:

Using Python with QiBuild projects
===================================

Under the cover, all the work is done using a
``virtualenv`` in the wortkree.

Step one: make sure the python projects can be found
----------------------------------------------------

First you have to make sure you have a correct ``qiproject.xml``, and
a ``setup.py`` next to it.

Also make sure to use ``qi_create_python_ext`` or ``qi_swig_wrap_python``
if you want your python extensions to be found

Something looking like

.. code-block:: xml

  <project version="3">
    <qibuild name="b_ext">
    <qipython name="b" />
  </project>

.. code-block:: cmake

  qi_create_python_ext(b b.c)
  # or
  qi_swig_python(b b.i b.c)

.. code-block:: python



  import os
  from setuptools import setup, find_packages

  setup(name="b",
        version="0.1",
        py_modules=['b'],
  )



Some useful links:

* `Learning about setup.py <https://docs.python.org/2/distutils/index.html>`_

* `Learning about virtualenv <https://virtualenv.pypa.io/en/latest/>`_

Your project should now be listed when running ``qipy list``

Step two: Use `qipy configure`
-------------------------------

This will initialize a virtualenv in the wortkree, and should be run
when changing or adding new python projects.

You can use a ``-c`` option to have several virtualenv in the wortkree.

The virtualenv will be initialized using ``pip install --editable``, so you
will be able to run your python code directly from the sources

Step three: using the virtualenv
---------------------------------

Just use ``qipy run`` instead of ``python``

``qipy run [-c config] foo.py``

