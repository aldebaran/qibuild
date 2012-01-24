.. _parsing-toolchain-feeds:

Parsing toolchain feeds
=======================

Let's assume you have a cross-toolchain updated to
http://example.com/packages/foo-ctc.tar.gz, a binary packge in
http://example.com/packages/bar.tar.gz, and a xml feed
looking like:

.. code-block:: xml

    <toolchain>
      <package
        name="foo-ctc"
        url="http://example.com/packages/foo-ctc.tar.gz"
        toolchain_file="cross-config.cmake"
      />
      <package
        name="bar"
        url="http://example.com/packages/bar.tar.gz"
      />

accessible in ``http://example.com/feeds/cross.xml``

And you run

.. code-block:: console

   $ qitoolchain create cross-foo http://example.com/feeds/cross.xml



See :py:mod:`qitoolchain.feed` for how XML parsing is done.

After every package has been parsed and added to the toolchain,
it is just a matter of ``toolchain.update_toolchain`` so
that the toolchain file is regenerated.

The toolchain file will then look like:

.. code-block:: cmake

    # Autogenerted file
    include("/path/to/a/ctc/cross-config.cmake")
    list(INSERT CMAKE_FIND_ROOT_PATH 0 "/path/to/a/ctc")
    list(INSERT CMAKE_FIND_ROOT_PATH 0 "/path/to/a/package")

and ``cross-foo`` will be added to the name of the known toolchains.

Then, when using

.. code-block:: console

   $ qibuild configure -c cross-foo my_project


A :py:class:`qibuild.toc.Toc` object will be created, containg a :py:class:`qitoolchain.toolchain.Toolchain` because
``cross-foo`` is a known name.

Then, a build directory name ``build-cross-foo`` will be created, and cmake will
be called, as if you had type:

.. code-block:: console

   $ cd ~/src/my_project/
   $ mkdir build-cross-foo
   $ cmake -DCMAKE_TOOLCHAIN_FILE=~/.cache/qi/toolchains/cross-foo.cmake ..


And everything will just work:

You will go throught the ``cross-config.cmake``, so the compiler to use will be
properly set, and you will have a entry in ``CMAKE_FIND_ROOT_PATH`` to where the ``bar`` package
has been extracted, so findingg ``bar`` libraries from the ``bar`` package will also work.

