.. toctree::
    :hidden:

    overviews/parsing_cmdline
    overviews/handling_build_configurations
    overviews/handling_cmake_flags
    overviews/parsing_toolchain_feeds


.. _qibuild-python-design:

qiBuild Python framework design
===============================


General design decisions
------------------------

qiBuild Python framework is designed around a few principles:

* Be modular : it should be easy to extend the command line
  API

* Have loosely-coupled, isolated components. This allows us to:

    * Easily write automatic tests
    * Easily refactoring code when there is a need to it.

* Have a nice user interface. This means:

    * Nice, helpful error messages
    * Colorful output when possible
    * Nice and always up-to-date built-in help
    * Let the use type less when possible

* Be intuitive: follow the principle of least surprise

* Prefer convention over configuration: configuration files should
  containing nothing more that necessary, and easy to generate
  automatically.


qiBuild **does** something non-standard, though: it forces use
to use the build directory it has generated for you.

This is the only way we can make sure the use will not end up mixing
build directories  (for instance mixing a 64 bits build directory
used to compile a library for your desktop, with a build directory
used when cross compiling).


.. _qibuild-python-concepts:

Concepts
--------

.. glossary::

   **action**
    Basically, the second argument of the `qibuild` command line.
    It always matches a python module.
    For instance, when calling `qibuild make`, we will be using
    the action named `qibuild.actions.make`.

.. seealso:

   * :ref:`parsing-cmdline`

.. glossary::

  **worktree**
    A worktree is simply a directory tree containing a ``.qi`` folder
    as its root. No more, no less.

.. seealso:

   * :py:mod:`qibuild.worktree`

Worktrees can be nested, although this is not recommended
(situation can get a little confused if you do so)

A worktree should also contain a ``qibuild.xml`` configuration
file.

.. seealso::

   * :ref:`qibuild-xml-syntax`


.. glossary::

  **Project**
    A qibuild project is simply a directory containing a
    ``qiproject.xml`` file at its root.
    The project must belong to a worktree, which means
    that one of the parent directories of the project directory
    must be a ``.qi`` directory.
    This simple algorithm means it's easy for qibuild to
    find project paths and names inside a worktree, but it
    also means you cannot have several projects with the
    same name inside the same worktree.

The name of the project is given inside the ``qproject.xml``
file, like this:

.. code-block:: xml

   <project name="foo" />

.. seealso::

   * :ref:`qiproject-xml-syntax`
   * :term:`project`

By convention, the name of the project matches the subdirectory
name, (that's what ``qibuild convert`` will do, for instance),
but this is not mandatory.

Note that although qibuild comes with a tool to manage several
git repositories (called qisrc), there is absolutely no problems
in having a project not in a git repositories, or several projects
inside the same directory.

Projects directory can be nested, but this is not recommended either.

Also note that nothing forces a qibuild project to be a CMake project.

We will just check that the project contains a root CMakeLists
when running `qibuild configure`, but that's all.

More specifically, we do NOT assume the project uses the qibuild
CMake framework.


.. glossary::

  **manifest**
    A manifest is simply a list of URL for projects.
    Right now only git URLs are supported, but conceptually
    nothing prevents you to use svn URL, or simply url to sources
    archives, and so on.

.. seealso::

   * :ref:`qisrc-manifest-syntax`


**toolchain**
  See :term:`toolchain` in the :ref:`qibuild-cmake-concepts` section.
  From qibuild point of view, every toolchain has a name and
  correspond to a specific configuration.



**Package**
  See :term:`package` in the :ref:`qibuild-cmake-concepts` section.
  From qitoolchain point of view, every package has a name
  and a path, and optionally a toolchain file.


.. glossary::

   **build configuration**

    A build configuration is just a name. Usually it matches a
    toolchain name, but you can also add:

     * some specific CMake flags
     * a specific CMake generator

    A build configuration is always associated to a build directory.
    You cannot have two different build configurations sharing
    the same build directory.

.. glossary::

  **Toc**
    A toc object is built from a working directory and a
    list of command line arguments.
    The name of the class comes from the first name of qibuild,
    which was a recursive acronym: 'TOC means Obvious Compilation'

.. seealso::

   * :py:mod:`qibuild.toc`


qibuild Python packages documentation
-------------------------------------

See :ref:`qibuild-python-doc` for a documentation of the
main packges, classes and functions of the qiBuild Python
Framework.


Overviews
---------

You can read the following sections if you want to understand deeply
how the qibuild command line tools work under the hood.

  * :ref:`parsing-cmdline`
  * :ref:`handling-build-configurations`
  * :ref:`parsing-toolchain-feeds`
  * :ref:`handling-cmake-flags`


