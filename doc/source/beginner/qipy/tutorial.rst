.. _qipy_tutorial:

Using Python with QiBuild projects
===================================

Under the cover, all the work is done using a
``virtualenv`` in the wortkree.

Step one: make sure the python projects can be found
----------------------------------------------------

First you have to make sure you have a correct ``qiproject.xml``, looking like

.. code-block:: xml

  <project version="3">
    <qipython name="THE NAME" />
  </project>

Some useful links:

* `Learning about setup.py <https://docs.python.org/2/distutils/index.html>`_

* `Learning abouth virtualenv <https://virtualenv.pypa.io/en/latest/>`_

Your project should now be listed when running ``qipy list``

Step two: Use `qipy configure`
-------------------------------

This will initialize a virtualenv in the wortkree.

You can use a ``-c`` option to have several virtualenv in the wortkree.

The virtualenv will be initialized using ``pip install --editable``, so you
will be able to run your python code directly from the sources

Step three: using the virtualenv
---------------------------------

Just use ``qipy run`` instead of ``python``

``qipy run [-c config] foo.py``
