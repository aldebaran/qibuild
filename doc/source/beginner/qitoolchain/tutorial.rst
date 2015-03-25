.. _qitoolchain-tutorial:

Managing pre-compiled binary packages with qitoolchain
=======================================================

When to use pre-compiled packages
---------------------------------

Pre-compiled packages are useful for third-party libraries.
For instance, if your code depends on ``boost``, you may want to make sure
that you are using a specific version of ``boost``, regardless of whatever
version may be already installed on the user machine.

Also, you may want to provide users of your software with pre-compiled packages, because
you do not want to share the source code, or to save some compilation time.

Creating packages
-----------------

If the project is using ``qibuild``, all you have to do is to run

.. code-block:: console

  qibuild package

If not, you have to create the package by hand. Assuming you want
to create a pre-compiled package for the ``foo`` library which uses
``autotools`` and depends on the ``bar`` library:

.. code-block:: console

    tar xvfz foo-src.tar.gz
    # Configure, build and install the library as usual:
    ./configure
    make
    DESTDIR=/tmp/foo make install
    cd /tmp/foo

Now that the project is installed, prepare it so that it follows the
correct layout:

.. code-block:: console

    mv usr/local* .
    rmdir -p usr/local


.. code-block:: console

    foo
       lib
         libfoo.so
       include
          foo.h


Then write a CMake module so that the foo library can be found:

.. code-block:: console

    cd /tmp/foo
    qibuild gen-cmake-module --name foo .

This will generate a file named ``foo-config.cmake`` in
``share/cmake/foo/foo-config.cmake``, that you can edit so that it looks like:

.. code-block:: cmake


    set(_root "${CMAKE_CURRENT_LIST_DIR}/../../..")
    get_filename_component(_root ${_root} ABSOLUTE)

    set(FOO_LIBRARIES
      ${_root}/lib/libfoo.so
      CACHE INTERNAL "" FORCE
    )

    set(FOO_INCLUDE_DIRS
      ${_root}/include
      CACHE INTERNAL "" FORCE
    )

    qi_persistent_set(FOO_DEPENDS "BAR")
    export_lib(FOO)


Then write a ``package.xml`` file looking like:

.. code-block:: xml

    <!--- in /tmp/foo/package.xml -->
    <package name="foo" version="0.1" target="linux64" >
      <depends buildtime="true" runtime="true" names="bar" />
    </package>

Finally, zip the package:

.. code-block:: console

    cd /tmp/foo
    zip foo-0.1.zip -r .

Excluding files at installation
-------------------------------

Say you are creating a binary package for Qt on Windows:

You do not want to include all the compilation tools (such as ``moc``, ``rcc`` or ``uic``)
when you install a project that has a runtime dependency on Qt.

But you still want to include ``lrelease``, ``lupdate`` because your application uses
these tools at runtime.

You also want to remove all the debug ``.dll`` when you install your application in
release mode.

The solution is to create masks in the package looking like this:

.. code-block:: console

    # in /path/to/Qt/runtime.mask

    # Remove all tools
    exclude bin/.*\.exe

    # But keep lrelease, lupdate:
    include bin/lrelease\.exe
    include bin/lupdate\.exe


    # in /path/to/Qt/release.mask

    exclude lib/.*d\.dll

Blank lines and comments starting with ``#`` are ignored.
Other lines should contain the word ``include`` or ``exclude``,
followed by a regular expression.


Creating a toolchain feed
--------------------------

You will need a place to host the packages and the feeds. It can be a simple
HTTP or FTP web server.

Let's assume you have ``foo`` and ``bar`` packages. Write a feed looking like

.. code-block:: xml

  <toolchain>
    <package name="foo" version="0.1" url="http://example.com/foo-0.1.zip" />
    <package name="bar" version="0.2" url="http://example.com/bar-0.2.zip" />
  </toolchain>


Using a toolchain
-----------------

Once the feed has been created, run:

.. code-block:: xml

  qitoolchain create my-toolchain http://example.com/feed.xml

And use:

.. code-block:: console

  qibuild add-config my-toolchain --toolchain my-toolchain
  qibuild configure -c my-toolchain


Importing binary packages
--------------------------

``qitoolchain`` also has support for importing binary packages coming from the ``gentoo``
distribution.

.. code-block:: console

    qitoolchain import-package -t my-toolchain --name foo /path/to/foo.tbz2
