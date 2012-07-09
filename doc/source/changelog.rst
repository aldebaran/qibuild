.. _qibuild-changelog:

Changelog
=========


1.16
----


Command line
+++++++++++++


* Nicer output for a few commands like ``qibuild test``.
* Add a lot of short options ("-n" for "--dry-run", "-f" for "--force")
* ``qibuild init``: add a ``--config`` argument to set the default config used by
  the worktree
* ``qidoc`` by-pass sphinx-build bug on mac
* ``qidoc`` make it work on archlinux  (using sphinx-build2 by default)
* Add ``qidoc open`` to view generated documentation in a web browser
* Add ``qidoc list`` list the known documentation projects in a wortree
* ``qitoolchain list`` better error message when there is no toolchain
* ``qidoc build`` improve argument parsing, smarter when no argument is given,
  can build a doc project by passing its name
* Add ``qisrc remove-project``
* Add ``qisrc add-project`` : projects are no longer automatically added in the wortree.
  (Should probably be merged with ``qisrc add``)
* Add ``qisrc list`` list the projects paths of a worktree
* Add ``qisrc grep`` to grep on every porject of a worktree
* Add ``qicd`` (inspired by ``roscd``)
* ``qisrc init`` can now be used with a git url (git@foo:manifest.git) (ala repo)
* ``qisrc init`` : add ``-p,  --profile`` option to choose from several profiles  (different xml files in the git url)
* ``qisrc init`` : add ``-b, --branch`` option to choose a branch in the manifest url
* ``qisrc status`` : now also display a message when the current branch is ahead or behind the remote branch
* Add ``qsrc sync`` : configure local and remote branches, automatically setup code review
* Add ``qisrc push`` : upload changes to code review
* Remove ``qisrc fetch``, use ``qisrc init`` instead
* Add ``qibuild deploy``, to deploy code to a remote device


CMake
++++++

* qibuild cmake modules:

  * added openssl, libevent_openssl

* added :cmake:function:`qi_generate_src`,  :cmake:function:`qi_generate_header`

Python
+++++++

* :py:func:`qibuild.config.read` add ``create_if_missing`` option
* ``install-qibuild.sh`` now installs ``qibuild`` scripts in ``~/.local/bin``
* :py:meth:`qisrc.git.Git.call` fix using ``quiet=True`` with ``raises=False``
* :py:meth:`qisrc.git.get_current_branch` : return None when in 'detached HEAD' state
* Add :py:mod:`qixml` to help XML parsing, get rid of ``lxml`` dependency
* :py:func:`qibuild.command.call` add ``quiet`` option
* Remove usage of ``qibuild.log`` and ``logging.py`` to display nice colorized messages
  to the console, use ``qibuild.ui`` module.

Misc
+++++

* Now using `tox <http://tox.readthedocs.org/en/latest/>` to run the tests on Jenkins,
  get rid of ``run_tests.py``
* Now using `py.test <http://pytest.org/latest/>` to write the automatic tests


1.14
----

Command line
+++++++++++++

* lots of bug fixes for XCode
* do not force CMAKE_BUILD_TYPE to be all upper-case. Now CMAKE_BUILD_TYPE equals
  ("Debug" or "Release"). Note that the build folder name did not change
  (It's still `build-<config>-release` when using `qibuild configure --release`)
* do not fail if default config is non existent
* qitolchain: now can set cmake generator from the feed.
* qitolchain: preserve permissions when using `.zip` packages on linux and mac
* mechanism to copy dlls inside the build dir and create the symlinks
  at the end of the compilation is now done by the qibuild executable,
  and NOT from the CMakeList.
* ``qibuild help``: sort available actions by name
* ``qibuild test``: small bug fix for ``--test-name``
* ``qibuild config --wizard``: fix unsetting build dir or sdk dir
* ``qibuid config --wizard:``: fix generator discovery for cmake 2.8.6 under windows
* ``qibuild configure``: nicer error message when cmake segfaults
* ``qibuild configure``: add ``--debug-trycompile`` option
* ``qibuild package`` : add ``--include-deps`` option
* ``qidoc``: fix for archlinux
* ``qibuild configure``: you can now use ``-c system`` if you have a default
  config in your worktree but still do not want to use it
* qitolchain: add ``import-package`` action able to import binary packages into
  a cross-toolchain.

CMake
+++++

* add :cmake:function:`qi_sanitize_compile_flags`
* :cmake:function:`qi_use_lib` sort and remove duplicates of include dirs
* :cmake:function:`qi_stage_lib`: allow adding custom_code
* :cmake:function:`qi_stage_bin` is now implemented
* :cmake:function:`qi_stage_header_only_lib` using ``DEPENDS`` did not work
* :cmake:function:`qi_stage_lib`: changed the way ``STAGED_NAME`` works.
* :cmake:function:`qi_use_lib`: optimize dependency handling

* ``swig/python``: keep number of include dirs reasonable
* ``target`` get rid of 'STAGE' args for ``qi_create_*`` functions
* ``install``: support for macosx bundles

* qibuild cmake modules:

  * added qtopengl, qtmultimedia, qt_phonon, eigen3, iphlpapi
  * now using upstream ``FindQt4.cmake`` to find `qt` when `qmake` is in PATH.
  * now using using ``FindBoost.cmake``
  * zeromq:   add dependency on RT for linux
  * libevent: add dependency on RT for linux

Python
++++++

* add :py:func:`qibuild.sh.change_cwd`
* add :py:func:`qibuild.sh.is_executable_binary`
* :py:mod:`qisrc.git` : rewrite
* :py:func:`qibuild.cmdparse.run_action` : allow adding ``--quiet-commands``
* add :py:func:`qitoolchain.binary_package` : provide functions to open binary
  packages
* add :py:func:`qitoolchain.binary_package.core` : abstract class for binary
  package provided by standard Linux distribution
* add :py:func:`qottolchain.binary_package.gentoo` : binary package class for
  *Gentoo* package (does not depends on *portage*)
* add :py:func:`qottolchain.binary_package.gentoo_portage` : binary package
  class for *Gentoo* package taking benefit from *portage*
* :py:func: `qibuild.archive.extract` , :py:func: `qibuild.archive.extract_zip` ,
  :py:func: `qibuild.archive.extract_tar` : add ``quiet`` keyword argument
  allowing non-verbose extraction
* :py:func: `qibuild.archive.extract_tar` : fix archive name guessing
* :py:func: `qibuild.interact` : add ``get_editor`` function

Misc
++++

* lots of documentation updates


1.12.1
------

Command line
++++++++++++

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
+++++

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
+++++++++++++++++++

* Use XML configuration everywhere, conversion is done by qibuild on the fly
  for .qi/qibuild.cfg and <project>/qibuild.manifest
* Path in the configuration files are now **preprend** to the
  OS environment variables instead of being appended.
* Add a small tool to convert to new XML config (tools/convert-config)

Python
++++++

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
+++++

* Cleanup installation of qibuild itself with cmake
* tests: rewrite python/run_test.py using nose
* Makefile: allow usage of PYTHON environment variable
* python/bin/qibuild script is usable as-is
* Lots of documentation updates


1.12
-----

First public release
