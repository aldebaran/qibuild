qiBuild : the build framework
=============================

qiBuild is a generic framework that helps for managing several projects
and their dependencies.

It comes with a set of tools:


qibuild : C++ compilation made easy
------------------------------------


qiBuild aims to make compilation of your sources easy. It manages dependencies
between projects and supports cross-compilation.

By default qiBuild uses libraries provided by your system, but you can also use
qiToolchain to manage sets of pre-compiled packages (called toolchains) if you
want. Cross-compilation is then just a matter of using a specific toolchain.

qiBuild is truly cross-platform: it is tested on Linux, Mac and Windows. Being
based on the well-known CMake build system, it allows you to use your existing
tools such as gcc, Make, or Visual Studio.

The qiBuild framework tries hard to stand out of your way: it remains close to
standards, and will play nice with other build systems.

qiBuild is composed of two parts:

* the qiBuild CMake framework, that simplifies authoring CMakeLists.txt.

* the qibuild/qitoolchain command line tools, that helps build projects while
  taking dependencies into account and generate re-distributable binary
  packages

Is qibuild the only one build framework?
++++++++++++++++++++++++++++++++++++++++


Of course not!

You can have a loot at

.. toctree::
   :maxdepth: 1

   other/cmake
   other/rosbuild
   other/qmake
   other/autotools


qisrc : Managing git projects
-----------------------------

The motivation for ``qisrc`` is to make it possible to work
with several git repositories at the same time.

Notes:
 * Yes, we are aware that git submodules exists, but we wanted
   something more flexible and easier to use

 * ``qisrc`` has more or less the same features than ``repo``,
   (including ``gerrit`` support for code review), but, contrary
   to ``repo``, it preserves a clean branch for you to work in
   and you can still use ``git`` normally


qidoc : Building documentation
------------------------------

``qidoc`` is a small tool that helps you write documentation in
``sphinx`` or in ``doxygen``, spread across several projects,
while making sure you can generate re-locatable HTML documentation


qilinguist: Translating projects
---------------------------------

``qilinguist`` makes it easier to use ``gettext`` in a CMake-based
project

