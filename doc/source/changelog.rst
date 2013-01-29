.. _qibuild-changelog:

Changelog
=========


Upcoming release
-----------------


Command line
+++++++++++++

* ``qibuild make``: add ``--coverity`` option to build with cov-analisys.
* ``qibuild clean``: syntax closer to other commands, cleans deep by default and
   respects ``--config`` ``--single`` and [project] options
* Nicer output for all commands.
* ``qibuild configure``: add a ``--summarize-options`` argument to
   print a summary of the build options at the end of the configuration
* ``qibuild configure``: add  ``--trace-cmake`` to trace CMake function calls
* ``qibuild make`` get rid of confusing and useless "--target" option
* Added a lot of short options ("-n" for "--dry-run", "-f" for "--force")
* ``qibuild init``: add a ``--config`` argument to set the default config used by
  the worktree
* ``qibuild``: improve argument parsing.

  * Do not configure everything when running ``qibuild configure`` from an unknown subdirectory
  * Automatically add projects to the worktree when running ``qibuild configure`` for a project
    not yet added to the worktree
  * qibuild commands now accepts both project names and project paths

* ``qibuild``: change dependency resolution

  * Now take both build dependencies and runtime dependencies into account by default.
    Use ``--build-deps`` to get only the build dependencies.

* ``qidoc`` by-pass sphinx-build bug on mac
* ``qidoc`` make it work on archlinux  (using sphinx-build2 by default)
* Added ``qidoc open`` to view generated documentation in a web browser
* Added ``qidoc list`` list the known documentation projects in a worktree
* ``qitoolchain list`` better error message when there is no toolchain
* ``qidoc build`` improve argument parsing, smarter when no argument is given,
  can build a doc project by passing its name
* Added ``qisrc remove``
* Added ``qisrc list`` list the projects paths of a worktree
* Added ``qisrc grep`` to grep on every project of a worktree
* Added ``qicd`` (inspired by ``roscd``)
* ``qisrc init`` can now be used with a git url (git@foo:manifest.git) (ala repo)
* ``qisrc init`` : add ``-p,  --profile`` option to choose from several profiles  (different xml files in the git url)
* ``qisrc init`` : add ``-b, --branch`` option to choose a branch in the manifest url
* ``qisrc status`` : now also display a message when the current branch is ahead or behind the remote branch
* Added ``qisrc sync``

  * configure local and remote branches
  * automatically setup code review
  * automatically synchronize git submodules

* Added ``qisrc push`` : upload changes to code review
* Added ``qibuild deploy``, to deploy code to a remote device
* ``qibuild test``: learned ``--slow``
* ``qibuild test``: learned ``-n, --dry-run`` to  just list the test names
* ``qibuild test``: learned ``--perf`` to run performance tests
* ``qibuild test``: ``--test-name`` has been removed, use ``-k PATTERN``
* Removed ``qisrc fetch``, use ``qisrc init`` instead
* Removed ``qisrc pull``, use ``qisrc sync`` instead
* Added ``qitoolchain convert-package``, to turn a binary package into a qiBuild package
* Added ``qitoolchain convert-package``, to turn a binary package or  package
  directory into a qiBuild package
* ``qitoolchain import-package`` learned ``--batch``
* ``qitoolchain import-package`` learned to import package directory
* :cmake:function:`qi_add_test` can now handle test script as target instead of binary.
* ``qibuild make`` learned ``--verbose-make``
* ``qisrc`` learned ``reset``

CMake
++++++

* Added :cmake:function:`qi_generate_src`,  :cmake:function:`qi_generate_header`
* Added :cmake:function:`qi_swig_wrap_java`
* Added :cmake:function:`qi_install_python`
* Added :cmake:function:`qi_create_perf_test`
* :cmake:function:`qi_create_gtest` and :cmake:function:`qi_create_test` learned
  the ``SLOW`` keyword so that tests are not run by default.
* :cmake:function:`qi_use_lib` learned the ``ASSUME_SYSTEM_INCLUDE`` flag
  to use ``-isystem`` on the dependencies
* :cmake:function:`qi_create_config_h` learned to use ``configure_file`` flags
  such as ``@ONLY``
* :cmake:function:`qi_install_conf` learned to install configuration files in a
  SYSCONDIR outside the CMAKE_INSTALL_PREFIX subtree.

  .. code-block:: console

    $ qibuild configure foo
    $ qibuild install foo --prefix=/usr /tmp/without_sysconfdir
    $ tree /tmp/without_sysconfdir
    /tmp/without_sysconfdir/
        usr/
            etc/
                foo.conf
            lib/
                libfoo.so

    $ qibuild configure foo -D SYSCONFDIR=/etc
    $ qibuild install foo --prefix=/usr /tmp/with_sysconfdir
    $ tree /tmp/with_sysconfdir
    /tmp/with_sysconfdir/
        etc/
            foo.conf
        usr/
            lib/
                libfoo.so

* :cmake:function:`qi_swig_wrap_python` learned to install python modules in the
  standard location
* qibuild cmake modules:

  * Added ``hdf5``, ``openssl``, ``libevent_openssl``,
    ``qt_qtdbus``, ``qt_qttest``, ``boost_unit_test_framework``,
    ``boost_test_exec_monitor``, ``boost_timer``, ``boost_chrono``,
    ``rrd``, ``rrd_th``, ``jsoncpp``, ``zbar``
  * Renamed dbus into dbus-1, and dbus-glib into dbus-glib-1
  * ``qi_use_lib(OPENGL)`` now uses upstream's ``FindOpenGL.cmake``
  * ogre-tools: Allow to use more than one plugin.

Python
+++++++

* Added :py:mod:`qisrc.sync` for synchronizing a worktree with a manifest
* Added :py:mod:`qisrc.review` for configuring a project to use gerrit
* Added :py:mod:`qibuild.deploy` to handle deploying code to a remote target
* Added :py:mod:`qibuild.gdb` to allow stripping debug symbols out of the libraries
* Added :py:mod:`qibuild.ui` for tools to interact with the user
* Added :py:mod:`qixml` to help XML parsing, get rid of ``lxml`` dependency
* Added :py:func:`qisrc.git.get_repo_root`
* Added :py:func:`qisrc.git.is_submodule`
* Renamed `qisrc.worktree.worktree_open` to :py:func:`qisrc.worktree.open_worktree`
* Renamed ``qibuild.worktree`` to :py:mod:`qisrc.worktree`
* :py:meth:`qibuild.config.QiBuildConfig.read`: learned ``create_if_missing`` option
* ``install-qibuild.sh`` now installs ``qibuild`` scripts in ``~/.local/bin``
* :py:meth:`qisrc.git.Git.call` fix using ``quiet=True`` with ``raises=False``
* :py:meth:`qisrc.git.Git.get_current_branch` : return None when in 'detached HEAD' state
* :py:func:`qibuild.command.call` learned ``quiet`` option
* Usage of ``qibuild.log`` and ``logging.py`` has been deprecated, use :py:mod:`qibuild.ui` instead
* ``toc.test_project`` has been removed, use :py:mod:`qibuild.ctest` instead
* ``toc.resolve_deps`` has been removed, use :py:func:`qibuild.cmdparse.deps_from_args` instead
* :py:meth:`qisrc.git.get_current_branch` : return None when in 'detached HEAD' state
* Add :py:mod:`qixml` to help XML parsing, get rid of ``lxml`` dependency
* :py:func:`qibuild.command.call` add ``quiet`` option
* Remove usage of ``qibuild.log`` and ``logging.py`` to display nice colorized messages
  to the console, use ``qibuild.ui`` module.
* Refactoring of the whole module ``qibuild.archive``:

  * Non-compatible APIs
  * Removed APIs:

    * :py:func:`qibuild.archive.extracted_name`
    * :py:func:`qibuild.archive.archive_name`
    * :py:func:`qibuild.archive.extract_tar`: use :py:func:`qibuild.archive.extract` instead
    * :py:func:`qibuild.archive.extract_zip`: use :py:func:`qibuild.archive.extract` instead
    * :py:func:`qibuild.archive.zip`: use :py:func:`qibuild.archive.compress` instead
    * :py:func:`qibuild.archive.zip_unix`: use :py:func:`qibuild.archive.compress` instead
    * :py:func:`qibuild.archive.zip_win`: use :py:func:`qibuild.archive.compress` instead
  * New APIs:

    * :py:func:`qibuild.archive.compress`: include ``algo`` option, which is set
      to  ``zip`` when unspecified
    * :py:func:`qibuild.archive.guess_algo`: guessing the compression method
      from the archive extension

  * Updated APIs:

    * :py:func:`qibuild.archive.extract`:

      * support for the ``topdir`` option has been removed
      * add ``algo`` option, when unspecified ``algo`` is set to ``zip`` on all platform

* Added :py:mod:`qibuild.cmake.modules` to handle CMake module generation
* Renamed :py:mod:`qibuild.cmdparse` to :py:mod:`qibuild.script`
* :py:mod:`qibuild.cmdparse` now centralize the parsing of qibuild actions arguments
   (guessing project from working directory and so on)

Misc
+++++

* Now using `tox <http://tox.readthedocs.org/en/latest/>`_ to run the tests on Jenkins,
  get rid of ``run_tests.py``
* Now using `py.test <http://pytest.org/latest/>`_ to write the automatic tests


1.14.1
------

Command line
++++++++++++

* fix using ``qitolchain`` with an ftp server configured with a
  "root directory" in ``.config/qi/qibuild.xml``

1.14
----

Command line
+++++++++++++

* Lots of bug fixes for XCode
* Do not force CMAKE_BUILD_TYPE to be all upper-case. Now CMAKE_BUILD_TYPE equals
  ("Debug" or "Release"). Note that the build folder name did not change
  (It's still `build-<config>-release` when using `qibuild configure --release`)
* Do not fail if default config is non existent
* qitolchain: now can set cmake generator from the feed.
* qitolchain: preserve permissions when using `.zip` packages on linux and mac
* <echanism to copy dlls inside the build dir and create the symlinks
  at the end of the compilation is now done by the qibuild executable,
  and NOT from the CMakeList.
* ``qibuild help``: sort available actions by name
* ``qibuild test``: small bug fix for ``--test-name``
* ``qibuild config --wizard``: fix unsetting build dir or sdk dir
* ``qibuid config --wizard:``: fix generator discovery for cmake 2.8.6 under windows
* ``qibuild configure``: nicer error message when cmake segfaults
* ``qibuild configure``: learned ``--debug-trycompile`` option
* ``qibuild package`` : learned ``--include-deps`` option
* ``qidoc``: fix for archlinux
* ``qibuild configure``: learned use ``-c system`` where ther is a default config
  in ther current worktree but user still wants to use no toolchain.
* Added ``qitoolchain import-package`` to import binary packages into a
  cross-toolchain.

CMake
+++++

* Added :cmake:function:`qi_sanitize_compile_flags`
* :cmake:function:`qi_use_lib` Now sorts and remove duplicates of include dirs
* :cmake:function:`qi_stage_lib`: learned ``CUSTOM_CODE`` keyword
* :cmake:function:`qi_stage_bin` is now implemented
* :cmake:function:`qi_stage_header_only_lib` using ``DEPENDS`` did not work
* :cmake:function:`qi_stage_lib`: changed the way ``STAGED_NAME`` works.
* :cmake:function:`qi_use_lib`: optimized dependency handling

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
* add :py:mod:`qitoolchain.binary_package` : provide functions to open binary
  packages
* add :py:mod:`qitoolchain.binary_package.core` : abstract class for binary
  package provided by standard Linux distribution
* add :py:mod:`qitoolchain.binary_package.gentoo` : binary package class for
  *Gentoo* package (does not depends on *portage*)
* add :py:mod:`qitoolchain.binary_package.gentoo_portage` : binary package
  class for *Gentoo* package taking benefit from *portage*
* :py:func:`qibuild.archive.extract` , :py:func: `qibuild.archive.extract_zip` ,
  :py:func:`qibuild.archive.extract_tar` : add ``quiet`` keyword argument
  allowing non-verbose extraction
* :py:func:`qibuild.archive.extract_tar` : fix archive name guessing
* :py:func:`qibuild.interact` : add ``get_editor`` function

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
* Added a small tool to convert to new XML config (tools/convert-config)

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
