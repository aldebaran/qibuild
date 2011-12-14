.. _qisrc-manifest-syntax:

qisrc manifest syntax
=====================

General
-------

This file is used by the ``qisrc fetch`` command
to get a list of projects to fetch and add in the
current work tree.


.. warning:: Right now, only git URLs are supported.


An example may be

.. code-block:: xml

    <manifest>
      <project
        name = "foo"
        url  = "git://example.com/foo.git"
      />
    </manifest>



manifest node
-------------

The ``manifest`` node accepts two types of children

  * ``project`` node
  * And, recursively, a ``manifest`` node

When a manifest is found inside an other manifest, it should have an URL

For instance:

.. code-block:: xml

    <manifest>

      <manifest url="http://example.com/a_manifest.xml" />

    </manifest>

If two projects are found with the same name, only the last url will
be taken into account


project node
------------

The ``project`` node *must* have the following two attributes:

  * ``name``
  * ``url``


