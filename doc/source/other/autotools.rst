.. _qibuild-and-autotools:

qiBuild and autotools
=====================

Introduction
-------------

This section is targeted towards autotools users wanting to know more about
qiBuild

The comparison between CMake and autotools applies to qiBuild and autotools,
too.

So, in a nutshell, using qiBuild/CMake over autotools has the following
advantages:

* Usable on windows without using a POSIX compatibility layer such as mingw or
  cygwin

* Can be used with Visual Studio

* Easy support for cross-compilation

* Somewhat nicer syntax


Using qiBuild with autotools projects
-------------------------------------

Right now there are no plans to make it easier to use qibuild with autotools
projects.

Here are two small task that could be tackled, though. (Patches welcome!)


Finding autotools-based projects
++++++++++++++++++++++++++++++++

There is already support for autotools in CMake.

It looks like:

.. code-block:: cmake

    find_package(PkgConfig)
    pkg_check_modules(FOO foo-0.42)

Unfortunately, this does not work if foo-0.42.pc is in a toolchain, so
you cannot use it to cross-compile a library which depends on foo.

This may be fixed by patching `PkgConfig.cmake` to
set PKG_CONFIG_PATH to `CMAKE_FIND_ROOT_PATH` and `--prefix` to
`CMAKE_FIND_ROOT_PATH` when calling `pkg-config`.


Generating pkg config files
+++++++++++++++++++++++++++

Again, nothing hard to do here.

During the call to :cmake:function:`qi_stage_lib`, it should be easy to
generate the `.pc` file. All the information is already here.

