qitoolchain.toolchain -- Handling binary packages
==================================================

.. py:module:: qitoolchain.toolchain


A Toolchain is simply a set of binary :term:`packages <package>`.


qitoolchain.toolchain.Package
-----------------------------

.. py:class:: Package(name, path[, toolchain_file=None)

    A package simply has a name and a path.
    It may also be associated to a toolchain file, relative to its path


qitoolchain.toolchain.Toolchain
-------------------------------

.. py:class:: Toolchain(name)

    A toolchain is a set of packages

    If has a name that will later be used as 'build config'
    by the toc object.

    It has a configuration in ~/.config/qi/toolchains/<name.cfg>
    looking like:

    .. code-block:: ini

      [package foo]
      path = '~/.cache/share/qi/ .... '
      toolchain_file = '...'

      [package naoqi-sdk]
      path = 'path/to/naoqi-sdk'

    thus added packages are stored permanentely.

    .. py:attribute:: name

       The name of the toolchain

    .. py:attribute:: packages

       A list of :py:class:`Package` instances

    .. py:attribute:: toolchain_file

       The path to the generated toolchain file.
       Usually in ``.cache/qi/toolchains/<name>/toolchain-<name>.cmake)``)
       It sets ``CMAKE_FIND_ROOT_PATH`` and includes the necessary
       toolchain files, for instance:

       .. code-block:: cmake

          # Autogenerted file
          include("/path/to/a/ctc/cross-config.cmake")
          list(INSERT CMAKE_FIND_ROOT_PATH 0 "/path/to/a/ctc")
          list(INSERT CMAKE_FIND_ROOT_PATH 0 "/path/to/a/package")

    .. py:method:: get(package_name)

        Get the path to a package

    .. py:method:: add_package(package)

        Add a package to this toolchain

        :param package: A :py:class:`Package`
            instance

    .. py:method:: remove_package(name)

        Remove a package from this toolchain

    .. py:method:: remove

        Remove self.

        Clean cache, remove all packages, remove self from configuration

    .. py:method:: parse_feed(feed)

        Parse an xml feed, adding packages to self while doing so
        See :ref:`parsing-toolchain-feeds` and
        :py:mod:`qitoolchain.feed` for details


