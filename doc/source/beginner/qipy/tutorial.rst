.. _qipy-tutorial:

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

  qi_create_python_ext(mymodule mymodule.cpp)
  # or
  qi_swig_python(mymodule.i mymodule.cpp)


where ``mymodule`` is the name of the python module, ``mymodule.cpp`` are some
sources, and ``mymodule.i`` is the name of the swig interface file.


.. code-block:: python



  import os
  from setuptools import setup, find_packages

  setup(name="mymodule",
        version="0.1",
        py_modules=['mymodule'],
  )



Some useful links:

* `Swig <http://www.swig.org/>`_

* `virtualenv <https://virtualenv.pypa.io/en/latest/>`_

* `Writing a setup.py file <https://docs.python.org/2/distutils/index.html>`_


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

