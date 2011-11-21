.. _toolchain-feed-syntax:

Toolchain feed syntax
=====================

General
-------

This is used by the ``qitoolchain create`` command.

The root of the ``feed.xml`` should be ``toolchain``

The global xml file should look like this:

.. code-block:: xml

   <toolchain>

    <package
      name="foo"
      url="http://example.com/packages/foo-1.0.tar.gz"
      version="1.0"
    />

  </toolchain>


toolchain type
--------------

The ``toolchain`` node accepts three types of children:

* ``package`` type

* ``feed`` type

* ``select`` type (more on this later)

feed type
---------

The ``feed`` type can have a ``url`` attribute, pointing to an other feed.

This lets you include feeds inside other feeds.

.. code-block:: xml

    <!-- in feeds/full.xml  -->
    <toolchain>
      <feed url = "feeds/included.xml" />
    </toolchain>

.. code-block:: xml

    <!-- feeds/included.xml -->

    <toolchain>
      <!-- some other packages -->
    </toolchain>


package type
------------

The ``package`` type **must** have at least a ``name`` attribute.

Optionally, it can have a ``version`` and a ``arch`` attributes.

This lets you store several configuration and several versions of the
same package in the same feed

.. code-block:: xml

    <toolchain>
      <package name="world" arch="linux32" version="0.1" url="world-0.1-linux32.tar.gz" />
      <package name="world" arch="linux32" version="0.2" url="world-0.2-linux32.tar.gz" />
      <package name="world" arch="linux64" version="0.1" url="world-0.1-linux64.tar.gz" />
      <package name="world" arch="linux64" version="0.2" url="world-0.2-linux64.tar.gz" />
    </toolchain>


If it does not have an ``url`` attribute, it should have a ``directory`` attribute,
and then the package path will be **relative** to the feed path.


This lets you put several packages in a big archive (for instance
``my-sdk.tar.gz``), and give it to other developers.

Simply create a ``toolchain.xml`` at the root of the SDK, looking like

.. code-block:: xml

    <toolchain>
      <package name="my-sdk" directory="." />
    </toolchain>

If you need a toolchain file, (for instance because your are generating a
cross-toolchain), simply use the ``toolchain_file`` attribute

.. code-block:: xml

    <toolchain>
      <package name="my-ctc" directory="." toolchain_file="my-toolchain.cmake" />
    </toolchain>


The ``toolchain_file`` is relative to the path of the package.


Of course, nothing prevents you to create a feed letting developers getting
your cross-toolchain remotely.

.. code-block:: xml

    <toolchain>
      <package
      name="my-ctc"
      url="http://example.com/myctc.tar.gz"
      toolchain_file="my-toolchain.cmake"
      />
    </toolchain>



select type
-----------

Right now we have no need for this, but several
things might be implemented later:


.. code-block:: xml

    <!-- Force a given arch -->
    <select>
      <arch>linux32</arch>
    </select>

    <!-- or: -->
    <select arch="linux32" />

    <!-- blacklist a specific package:
      foo-1.12 will never be added
    -->
    <select>
      <blacklist name="foo" version="1.12" />
    </select>


    <!-- assert that a specific package
      is here
      If no bar-1.14 package is found, an
      error will be raised
    -->
      <select>
        <force name="bar" version="1.14" />
      </select>


We do not need this because when several packages are found,
we simply take the latest version.

So for instance, if you need ``foobar-0.1`` in your maintenance branch,
but ``foobar-2.0`` in your devel branch, you can simply have two feeds, like
this

.. code-block:: xml

    <!-- in maint.xml -->
    <toolchain>
      <package name="foobar" version="0.1" url="http://example.com/packages/foobar-0.1.tar.gz" />
      <package name="spam"   version="1.0" url="http://example.com/packages/spam-1.0.tar.gz" />
    </toolchain>

.. code-block:: xml

    <!-- in devel.xml -->
    <toolchain>
      <feed url="http://example.com/feeds/maint.xml" />
      <package name="foobar" version="2.0" url="http://example.com/packages/foobar-2.0.tar.gz" />
    </toolchain>



