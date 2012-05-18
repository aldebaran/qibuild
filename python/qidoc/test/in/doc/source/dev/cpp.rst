C++
===



.. code-block:: rst

    .. This does not work

    qibuild ref does not work like this: :ref:`qibuild:qibuild-aldeb`

But this does:

qibuild ref works like this: `Using qiBuild with Aldebaran Packages <../qibuild/qibuild_aldeb.html>`_


.. toctree::
    :hidden:

    tutos/cpp.rst


.. ifconfig:: build_type == "release"

   This is a public build of the doc, ready for release

.. ifconfig:: build_type == "internal"

   This is an internal build of the doc


This should produce an warning in internal doc,
but not in public doc:

.. toctree::

   does/not/exists
