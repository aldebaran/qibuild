.. _qibuild-relnotes:

qiBuild release notes
=====================

What's new in qibuild 1.12.1
-----------------------------

CMake
+++++

It is now much easier to port an existing CMake project to ``qibuild``

Just use

.. code-block:: cmake

   project(myproject)
   find_package(qibuild)


(No need for the ``qibuild.cmake`` file everywhere)

Configuration files
+++++++++++++++++++

Every configuration file used by qiBuild is now in XML.

``QI_WORK_TREE/.qi/qibuild.cfg`` is deprecated, use ``QI_WORK_TREE/.qi/qibuild.xml``
and ``~/.config/qi/qibuild.xml`` instead.

``<project>/qibuild.manifest`` is deprecated, use ``<project>/qiproject.xml>`` instead.

Note that conversion is done by qiBuild on the fly, but the XML file are only written
if they do not exist.


qidoc
+++++

* Add a new tool called ``qidoc``.

``qidoc`` lets you build nice documentation by using sphinx and doxygen
projects spread across several repositories, while keeping the
global settings (stylesheets, templates, etc.) in on place

.. warning:: qidoc is still a work in progress. It is used to build
   Aldebaran documentation, but the tool itself is quite hard to use
   for anything else right now


Full Changelog
--------------

1.12.1
++++++

Command line
~~~~~~~~~~~~

* qitoolchain: add support for password-protected HTTP and FTP feed URLS.
* Added ``qitoolchain clean-cache`` to clean toolchains cache
* Added ``qidoc`` executable (work in progress)
* Added ``qibuild find PACKAGE`` to display CMake variables relate to the package (work in progress)
* Added ``qibuild config --wizard`` to configure both global and local settings
* ``qibuild package``: always build in debug and in release on windows
* ``qisrc pull``: fix return code on error (#6343)
* ``qibuild config --edit`` : do not mess with stdin
* ``qibuild init --interactive`` now calls ``qibuild config --wizard``
* ``qibuild install``: force calling of 'make preinstall'
* ``qitoolchain update``: update every toolchain by default
* ``qibuild test``: use a custom CTest implementation instead of using
  the ``ctest`` executable. (Makes continuous integration much easier)
* ``qibuild package``: clean command-line API
* ``qibuild convert``: add ``--no-cmake`` argument
* ``qibuild convert``: do not add ``include(qibuild.cmake)`` if it is already here
* ``qisrc pull`` now call ``qisrc fetch`` first (#204)
* ``qitoolchain create``: prevent user to create bad toolchain names

CMake
~~~~~

* Better way of finding qibuild cmake framework, using ``find_package(qibuild)``
  instead of ``include(qibuild.cmake)``
* :cmake:function:`qi_create_gtest`: prefer using a qibuild port of gtest
* :cmake:function:`qi_create_gtest`: disable the target when gtest is not found
* :cmake:function:`qi_create_gtest`: always add GTEST dependency
* :cmake:function:`qi_stage_lib`, :cmake:function:`qi_use_lib` better handling when first arg is not
  a target
* :cmake:function:`qi_create_lib` did not honor NO_INSTALL argument
* ``qi_install_*`` functions no longer recurse through directories by default,
  use ``qi_install_*(... RECURSE)``
* Added :cmake:function:`qi_create_test` function, simpler to use than :cmake:function:`qi_add_test`
* Added new qibuild cmake modules:

  * lttng and its dependencies
  * opencv2
  * qtmobility, qtxmlpatterns, qt_qtscript, qtsvg
  * qxt-core, qtxt-newtork
  * pythonqt

Configuration files
~~~~~~~~~~~~~~~~~~~

* Use XML configuration everywhere, conversion is done by qibuild on the fly
  for .qi/qibuild.cfg and <project>/qibuild.manifest
* Path in the configuration files are now **preprend** to the
  OS environment variables instead of being appended.
* Add a small tool to convert to new XML config (tools/convert-config)

Python
~~~~~~

* Remove deprecated warning message when using python 2.6.1 on Mac
* qibuild.archive: by-pass python2.6 bugs
* qibuild.archive.zip_win: actually compress the archive
* qibuild.sh.to_native_path: follow symlinks
* qibuild.sh.rm : use rmtree from gclient
* qibuild.worktree: do not go through nested qi worktrees
* qibuild.command: use NotInPath in qibuild.call
* qibuild.toc.get_sdk_dirs: fix generation of dependencies.cmake in
  some corner cases
* qibuild.Project: add a nice __repr__ method
* qibuild does not crashes when an exception is raised which contains '%' (#6205)

Misc:
~~~~~

* Cleanup installation of qibuild itself with cmake
* tests: rewrite python/run_test.py using nose
* Makefile: allow usage of PYTHON environment variable
* python/bin/qibuild script is usable as-is
* Lots of documentation updates


1.12
+++++

First public release
