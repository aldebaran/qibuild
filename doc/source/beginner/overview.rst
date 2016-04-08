qiBuild: the build framework
============================

Basic concepts
--------------

qiBuild is a generic framework that helps for managing several projects
and their dependencies.

It comes with a set of tools, which are listed below.

Every tool comes with a matching script (``qibuild``, ``qisrc``, etc.),
and must be used from a :term:`worktree`.

Every project must be inside the worktree, and should have a ``qiproject.xml`` at
its root. This is how the scripts can find the projects paths when they look
for dependencies, for instance.

Read more about this in this section: :ref:`worktree-and-projects`.

So, in order to be able to use qiBuild scripts, you should first create
a worktree with ``qibuild init``, and then register projects paths with
``qisrc add``.

For instance:

.. code-block:: console

   cd ~/work
   qibuild init
   mkdir my_first_proj
   # edit my_first_proj/qiproject.xml
   qisrc add my_first_proj

Demo
----

.. raw:: html

  <script type="text/javascript"
          src="https://asciinema.org/a/35360.js"
          id="asciicast-35360" async>
  </script>


qibuild: C++ compilation made easy
----------------------------------


qibuild aims to make compilation of your sources easy. It manages dependencies
between projects and supports cross-compilation.

By default qibuild uses libraries provided by your system, but you can also use
qitoolchain to manage sets of pre-compiled packages (called toolchains) if you
want. Cross-compilation is then just a matter of using a specific toolchain.

qibuild is truly cross-platform: it is tested on Linux, Mac and Windows. Being
based on the well-known CMake build system, it allows you to use your existing
tools such as gcc, Make, or Visual Studio.

The qibuild framework tries hard to stand out of your way: it remains close to
standards, and will play nice with other build systems.

qibuild is composed of two parts:

* the qibuild CMake framework, that simplifies authoring CMakeLists.txt.

* the qibuild/qitoolchain command line tools, that helps build projects while
  taking dependencies into account and generate re-distributable binary
  packages.

What makes qiBuild different ?
++++++++++++++++++++++++++++++

The good parts
~~~~~~~~~~~~~~

* Full support for Visual Studio

* Full support for cross-compilation (hosts: linux, mac: targets : x86, arm, android, ...)

* Comes with a tool to use pre-compiled dependencies

* No environment variables required, and keep your environment clean

* Written in Python like many others but:

  * Python2/Python3 compatible

  * >80% test coverage

  * Only pure-Python dependencies, for easier installation on Windows

* Can find dependencies **from the sources**. For instance, in a worktree with
  two different CMake projects , ``world`` and ``hello``, when compiling ``hello``,
  we will find ``world`` headers directly from ``world`` sources.

* Automatic install rules (you have to *explicitly* exclude targets from installation)

* ``qibuild package --standalone`` generates an archive that is:

  * relocatable

  * and work across linux distributions

* Full Python support : you can write Python code that use extensions written in C++
  with ease, and run the C++ and the Python tests with the same tool

* Each project build dir contains a nice ``sdk`` folder with files where you expect them
  (``.dlls`` and ``.exe`` in ``sdk/bin``, ``.so`` in ``sdk/lib/`` and data in
  ``sdk/share``)

* You can deploy your code to a remote host via ``ssh`` and ``rsync``

* You can also deploy or install your tests, and then only run them with
  ``qitest``

The bad parts
~~~~~~~~~~~~~

* Requires a :term:`worktree`. So it's useless if you have only one project.

* Re-implements
  `CMake build system
  <https://cmake.org/cmake/help/latest/manual/cmake-buildsystem.7.html>`_

* Cannot directly use upstream ``Find*.cmake``` files, especially if they
  contained exported target (We have hacks for Qt5 because of this)

* Generated ``-config.cmake`` files could be used by other CMake code, but they
  contain a ``_DEPENDS`` variable that only ``qiBuild`` can understand.
  Also, they use old-style ``*_INCLUDE_DIRS``, ``*_LIBRARIES`` variables instead
  of modern exported targets

qibuild compared to other build frameworks
+++++++++++++++++++++++++++++++++++++++++++

Have a look at

.. toctree::
   :maxdepth: 1

   qibuild/other/cmake
   qibuild/other/ros
   qibuild/other/qmake
   qibuild/other/autotools


Going further with qibuild
++++++++++++++++++++++++++

Read more about qibuild in the :ref:`qibuild-tutorial`, or
follow the :ref:`qibuild-guide`.


qisrc: Managing git projects
----------------------------

The motivation for ``qisrc`` is to make it possible to work
with several git repositories at the same time.

Notes:
 * Yes, we are aware that git submodules exists, but we wanted
   something more flexible and easier to use.

 * ``qisrc`` has more or less the same features than ``repo``,
   (including ``gerrit`` support for code review), but, contrary
   to ``repo``, it preserves a clean branch for you to work in
   and you can still use ``git`` normally.


Tutorial
++++++++

See :ref:`qisrc-tutorial`.


qidoc: Building documentation
-----------------------------

``qidoc`` is a small tool that helps you write documentation in
``sphinx`` or in ``doxygen``, spread across several projects,
while making sure you can generate re-locatable HTML documentation.


Tutorial
++++++++

See :ref:`qidoc-tutorial`.


qilinguist: Translating projects
--------------------------------

``qilinguist`` provides tools to help internationalization
of any kind of project, using ``gettext`` or ``Qt Linguist``
as backend.

Tutorial
++++++++

See :ref:`qilinguist-tutorial`.

qipy: qibuild and Python
------------------------

``qipy`` makes it possible to use Python extensions
written in C/C++ with ``qibuild`` with pure Python libraries.

Tutorial
+++++++++

See :ref:`qipy-tutorial`.

qipkg: Generate binary packages
--------------------------------

``qipkg`` lets you make packages the same way Choregraphe does,
but from the command line, and also lets you embed code written in
C++ or Python inside the package.

Tutorial
++++++++

See :ref:`qipkg-tutorial`
