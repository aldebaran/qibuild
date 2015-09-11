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
      <license>BSD</license>
      <depends buildtime="true" runtime="true" names="bar" />
    </package>

.. note:: the ``<license>`` tag is not mandatory, but recommended

In the end the package tree should look like this:

.. code-block:: console

    foo
      package.xml
      lib
        libfoo.so
      include
        foo.h
      share
        cmake
          foo
            foo-config.cmake



Finally, create the package with ``qitoolchain make-package``

.. code-block:: console

    qitoolchain make-package /tmp/foo

Using cross-toolchains
-----------------------

Let's say you want to cross-compile for ARM. You should find:

* a cross-compiler
* a ``sysroot``
* a ``toolchain.cmake`` that calls ``CMAKE_FORCE_C_COMPILER`` and
  ``CMAKE_FORCE_CXX_COMPILER``

You should put all of this into a package, with a few additional metadata:

.. code-block:: console

  <ctc>
     package.xml
     sysroot
        etc
        usr
          include
      bin
        arm-linux-gnu-gcc
        arm-linux-gnu-g++
        arm-linux-gnu-gdb

.. code-block:: xml

    <!-- in package.xml -->
    <package name="arm-ctc"
             host="linux64"
             target="arm"
             version="r1"
             sysroot="sysroot"
             gdb="bin/arm-linux-gnu-gdb"
             toolchain_file="toolchain.cmake" />

Then you can use:

.. code-block:: console

  qitoolchain make-package ctc
  qitoolchain add-package arm-ctc-linux64-r1.zip

as you would do for a normal package.

Specifying custom flags
------------------------

Sometimes you just want to set some compile flags while building.
To do that, you can create a package that will set ``CMAKE_CXX_FLAGS`` for you.

For instance, to activate ``C++11`` support, you can create a ``c++11`` package

.. code-block:: console

  c++11
    package.xml
    config.cmake

.. code-block:: xml

  <!-- in package.xml -->
  <package name="c++11" toolchain_file="config.cmake" />

.. code-block:: cmake

  # in config.cmake

  set(CMAKE_CXX_FLAGS "-std=gnu++11" CACHE INTERNAL "" FORCE)


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


Alternatively, you can create a git repository to store your feed.
Just make sure it is in a 'feeds' subdirectory, like this:

.. code-block:: console

    <toolchains.git>
      feeds
        foo.xml


Using a toolchain
-----------------

Once the feed has been created, run:

.. code-block:: console

  qitoolchain create my-toolchain http://example.com/feed.xml

Or:

.. code-block:: console

  qitoolchain create my-toolchain --name foo git@example.com:toolchains.git

Here ``--name`` is the name of the feed in the ``feeds`` directory on the git
repository, without the ``.xml`` extension.

Then use:

.. code-block:: console

  qibuild add-config my-toolchain --toolchain my-toolchain
  qibuild configure -c my-toolchain


Importing binary packages
--------------------------

``qitoolchain`` also has support for importing binary packages coming from the ``gentoo``
distribution.

.. code-block:: console

    qitoolchain import-package -t my-toolchain --name foo /path/to/foo.tbz2


Putting binary packages in a subversion repository
---------------------------------------------------

Instead of hosting zips on a HTTP server, you may want to host the pre-compiled packages
in a subversion server. Why subversion ? Because it allows partial checkouts, and it
is not that bad at managing binary blobs.

You may have a layout like this on the server:

.. code-block:: console

   <svn root>
    master
        win32-vs2010
          boost
          qt
        linux64
          boost
          qt

Then you can specify packages in the XML feed using a ``svn_package`` element:

.. code-block:: xml

    <!-- in feeds/linux64.xml -->
    <feed>
      <svn_package name="boost" url="svn://example.org/toolchains/master/linux64/boost" />
      <svn_package name="qt" url="svn://example.org/toolchains/master/linux64/qt" />
    </feed>

When using ``qitoolchain create``, the packages will be created using ``svn checkout``, and
then ``svn update`` will be called when using ``qitoolchain update``.

You can also specify a revision inside the feed:


.. code-block:: xml

    <!-- in feeds/linux64.xml -->
    <feed>
      <svn_package name="boost" url="svn://example.org/toolchains/master/linux64/boost" revision="42" />
    </feed>


Using sub feeds
---------------

Let's assume you want to create several feeds for cross-compiling on several
operating systems. Each feed will contain a specific package for the
cross-compiler, which is host dependent, and a list of common packages for the
third-party libraries, which are host independent.

To solve this problem, you can include some feeds into an other one,
like this:

.. code-block:: console

    arm.xml
    linux64-arm.xml
    mac64-arm.xml

.. code-block:: xml

    <!-- in arm.xml -->
    <feed>
      <package name="boost" url="..." />
    </feed>

    <!-- in linux64-arm.xml -->
    <feed>
      <feed url="http://example.com/feeds/arm.xml" />
      <package name="ctc-linux64-arm" url="..." />
    </feed>

    <!-- in mac64-arm.xml -->
    <feed>
      <feed url="http://example.com/feeds/arm.xml" />
      <package name="ctc-mac64-arm" url="..." />
    </feed>

If you chose to put the feeds in a git repository, you can specify
sub feeds by name, like this

.. code-block:: xml

  <!-- in feeds/linux64-arm.xml -->
  <feed>
    <feed name="arm" />
    ...
  </feed>
