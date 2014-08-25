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


Is qibuild the only one build framework?
++++++++++++++++++++++++++++++++++++++++


Of course not!

You can have a loot at

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

