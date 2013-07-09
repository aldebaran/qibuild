.. _qibuild-changelog:

Changelog
=========

V3.0
-----

General
+++++++

* Tons of bug fixes, massive Python refactoring

* The ``./install-qibuild.sh`` script is gone: its name was misleading,
  and it lead to bad stuff, like:
  * installing in ``/usr/local`` by default on mac (which causes problem on
    a multi-user machine)
  * being hard to know which qibuild version was used

Instead, you should use ``./generate-sourceme.sh`` and patch your
``~/.profile`` to include the generated ``sourceme.sh`` file.

Command line
+++++++++++++

General
~~~~~~~

* Some actions that could only run on *all* projects learned a ``-p,--projects``
  argument. You can now for instance use ``qibuild foreach -p hello -- <cmd>``
  to run ``<cmd>`` on the ``hello`` project and its dependencies

* It is now impossible to have nested worktrees.

  * The ``--force`` option is gone
  * ``qibuild init``, ``qisrc init``, will only run if the working
    directory is empty

qisrc
~~~~~

* After ``qisrc init``, the projects under code review now
  end up with only one remote instead of two.
* ``qisrc init`` learned ``--groups`` to only clone some repositories
  of a project
* ``qisrc sync`` now always clones the missing projects (even when not using
  ``-a``)
* ``qisrc sync`` now handles repositories renames
* ``qisrc sync`` logic changed to be a bit more reliable and fail less often
* ``qisrc foreach`` learned ``--all``, to run on every projects (previously
  it could only run on git projects)
* add ``qisrc manifest`` to manage the manifest used in a given worktree.
* ``qisrc init`` can now only be used once. To add a new manifest, run
  ``qisrc manifest --add name url``. This makes it possible to change the groups,
  too
* ``qisrc init --no-review`` is gone, this was seldom used anyway
* ``qisrc sync`` learned ``--build-deps``  to pull the build dependencies
* Since this option clashes with other qibuild option, you should now use
  ``qibuild configure --no-runtime`` or ``qibuild configure --build-deps-only``
  instead of ``qibuild configure --build-deps``

qibuild
~~~~~~~

* ``qibuild`` now uses ``CMake`` code from the worktree. This makes it possible
  to use a Python command line version ``qibuild`` different of the ``qibuild/cmake``
  code.
* ``qibuild init -c`` is deprecated, use ``qitoolchain set-default`` instead
* ``qibuild init --interactive`` is deprecated, use ``qibuild config --wizard`` instead
* ``qibuild test`` learned ``--build-first``
* Add ``qibuild run``
* Add ``qibuild find``

qitoolchain
~~~~~~~~~~~

* Add ``qitoolchain set-default``

qilinguist
~~~~~~~~~~~

* ``qilinguist`` can now be called without any project name
* Add ``qilinguist list``


Config files
++++++++++++

* Manifests are now cloned in ``.qi/manifests``, making it possible to
  have code review on manifests repositories too
* Syntax of ``qiproject.xml`` changed:

.. code-block:: xml

    <!-- old -->
    <project name="foo">
      <depends runtime="true" names="bar" />
      <qidoc name="foo-doc" src="." />
    </project>

.. code-block:: xml

    <!-- new -->
    <project version="3" >
      <qibuild name="foo">
        <depends runtime="true" names="bar" />
      </qibuild>

      <qidoc name="foo-doc" />
    </project>

This is more consistent, and helps solving nasty bugs when using nested
qibuild projects.

* Syntax of the ``manifests.xml`` changed:

.. code-block:: xml

    <!-- old -->
    <manifest>
      <remote name="origin" fetch="git@example.com"
              review="http://gerrit:8080" />
      <project name="libfoo.git"
               path="lib/libfoo"
               revision="next"
               review="true" />
    </manifest>

.. code-block:: xml

    <!-- new -->
    <manifest>
      <remote name="origin" url="git@example.com" />
      <remote name="gerrit" url="ssh://gerrit:29418/" review="true" />

      <repo src="lib/libfoo" default_branch="next" remote="gerrit" />
    </manifest>

* The gerrit ssh port is now no longer hard-coded, and you
  should specify the ``ssh`` url, not the ``http`` url.
* The ``next`` branch of the repo in ``lib/libfoo``
  will track ``ssh://<username>@gerrit:29418/libfoo.git`` instead of
  ``git@example.com:libfoo.git``. This makes it possible to use gerrit only,
  without any mirror, and it also means you don't have to wait for the
  gerrit synchronization, which is hepful when using ``qisrc`` on a
  buildfarm plugged to gerrit.
* The default manifest is now called ``manifest.xml`` instead of ``default.xml`` to
  ease the transition.

* ``qisrc`` profiles are gone, use groups instead. Here's how you can make
  it possible to only clone 2 of the 3 repositories declared in the manifest:

.. code-block:: xml

  <!-- in qibuild2 -->

  <!-- manifest/default.xml -->

    <manifest>
      <project name="foo.git" />
      <manifest url="bar.xml" />
    </manifest>

  <!-- manifest/bar.xml -->
    <manifest>
      <project name="bar.git" />
      <project name="libbar.git" />
    </manifest>

Used with ``--profile bar``


.. code-block:: xml

  <!--in qibuild3 -->

    <manifest>
      <repo name="foo.git" />
      <repo name="bar.git" />
      <repo name="libbar.git" />

      <groups>
        <group name="bar">
          <project name="bar.git" />
          <project name="libbar.git" />
        </group>
      </groups>
    </manifest>

Used with ``--group bar``

CMake
+++++

* MacOS: use rpath: libraries use an ``@rpath`` based directory for the default
  installed name. Executables contain a rpath pointing to the root of the
  install directory.
* Linux shared libraries are linked with a RPATH set to ``$ORIGIN/../lib``
  by default, as it was done for executables.

v2.4
----

CMake
+++++

* ``qi_stage_script`` is now implemented, and it's now possible to stage Python scripts too.
* Add ``qi_generate_trampoline``
* ``qi_add_test`` now also uses ``find_program`` to find test executable.
* API break: you should now use ``BUILD_PERF_TESTS=OFF`` instead of ``BUILD_PERFS_TESTS=OFF``
  when you do not want to build the performance tests
* Fix using ``qi_add_perf_test`` on Windows when building in debug

v2.3
----

Command line
++++++++++++

* Add ``qisrc maintainer``
* Fix ``qibuild clean -z`` behavior
* Fix a bug where ``qbibuild make`` could create recursive symlinks
* ``qibuild clean`` learned ``-x`` to remove build directories that match no known configurations
* ``qibuild deploy`` now accepts url matching [[login]@]url[:[relative/path]] or url parseable with urlparse beginning with ssh:// only
* ``qibuild deploy`` no longer accepts a ``--port`` option, specify the port
  inside the url instead::

    # old
    qibuild deploy --port 23 user@host:path/to/remote/dir
    # new
    qibuild deploy ssh://user@host:32/full/path/to/remote/dir

* ``qibuild deploy``: project is no more a positional argument
* Positional url is no more mandatory in ``qibuild deploy``, and you
  can now deploy to several urls at once
* ``qibuild create`` no longer exists, use ``qisrc create instead``

CMake
-----

* ``qi_add_test`` now also accepts a package name as test binary
* qibuild cmake modules:

  * add ``boost-python``
  * ``python-config.cmake`` now longer searches or python2.6, and does not
    look for ``python_d`` even when building in debug. (this is required
    to make ``boost-python`` work when using Visual Studio)
  * bug fix when using ``find_package`` twice with a CMake module calling
    ``pkg_search_module`` (for instance with ``qi_add_optional_package``)
  * Implement ``qi_stage_script`` which was present but empty.

Python
++++++

* Add ``qisrc.maintainer`` to manage maintainers from ``qiproject.xml``
* Add ``qisys.ui.indent_iterable`` to indent list or any iterable
* ``qibuild.parsers.project_parser`` learn ``positional``
* Add ``qibuild.deploy.action.find_rsync_or_scp``
* ``qibuild.deploy.parse_url`` return a dict

V2.2
----

General
+++++++

* Update of the doc
* Remove compatibility with python 2.6
* You can now set the environment variable ``VERBOSE=1`` to trigger debug
  messages

Command line
++++++++++++

* ``qisrc sync``: Prevent unwanted rebases when we are already synced
* Fix return code of ``qibuild test --list``
* ``qilinguist``: Stop doing backup when merging catalog files
* ``qibuild test`` learn ``--ncpu`` to restrict the number of CPUs
* Tests are now colored under a tty
* ``qisrc grep`` learn ``--project`` to run only on some specific project
* ``qisrc foreach`` learn ``--project`` to run only on some specific project
* ``qisrc foreach`` learn ``--dry-run`` to dry run the command
* Fix using ``qibuild deploy`` to a remote folder containing upper-case letters

CMake
+++++

* Keep ``CMAKE_FIND_ROOT_PATH`` clean during incremental builds
* Fix using :cmake:function:`qi_add_optional_package` with a file defining some macros
* ``boost``: support 1.53, adapt ``boost_flib`` for libraries being only headers
* Fix perf tests with VisualStudio
* ``qi_create_gtest`` now only works with Aldebaran's fork of gtest
* ``qi_generate_src`` can now generate several files with one command

Python
++++++

* Move ``qixml`` to ``qisys``
* ``XMLParser`` now take a ``target``
* ``qitoolchain`` now update toolchain instead of deleting and create

V2.1
----

Command line
++++++++++++

* Add ``qilinguist``.
* ``qisrc reset`` learn ``--fetch``  and ``--no-fetch``.
* ``qisrc snapshot`` learn ``--fetch``, ``--no-fetch`` and ``--tag``.
* ``qisrc list`` learn ``--with-path``.
* ``qisrc grep`` learned ``-path``.
* ``qisrc clean`` learned ``-z`` to clean build dir through toolchains and profiles.
* ``qibuild test``: learned ``--ncpu`` to restrict the number of CPUs a test can use using taskset if available

CMake
+++++

* Added :cmake:function:`qi_stage_dir`

Python
++++++

* Add ``qisrc.sync.get_toplevel_git_projects`` to ignore submodules
  in a project list.
* Add functions for handle build projects in qibuild and remove them from
  ``qisys.worktree``.

  * ``qibuild.project.is_buildable``.
  * ``qibuild.project.build_projects``.

* Add functions for handle git projects from ``qisys.worktree`` to
  ``qisrc.git``.

  * ``qisrc.git.is_git``.
  * ``qisrc.git.get_git_projects``.

* ``qibuild.parsers.build_parser`` has been split.

  * ``qisrc.parsers.build_type_parser`` is for know the type of build
    and so the name of the build directory.
  * ``qisrc.parsers.build_parser`` extend the previous one and add
    option for build projects (as ``-j``).

* Remove ``qibuild.archive`` use ``qisys.archive`` instead.
* Add ``qibuild.toc.get_build_folder_name`` to get the name of a build
  directory from some informations.
* Add ``qibuild.toc.Toc.get_build_folder_name`` to get the name of
  the build directory from a toc.
* Remove ``qibuild.toc.set_build_folder_name`` and
  ``qibuild.toc.Toc.build_folder_name``
* Add ``qibuild.toc.has_project``.

V2.0
----

Command line
++++++++++++

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
* ``qibuild make`` learned ``--verbose-make``
* ``qisrc`` learned ``reset``
* ``qisrc`` learned ``snapshot``

CMake
++++++

* Added :cmake:function:`qi_generate_src`,  :cmake:function:`qi_generate_header`
* Added :cmake:function:`qi_swig_wrap_java`
* Added :cmake:function:`qi_install_python`
* Added :cmake:function:`qi_stage_dir`, to find files from source directories
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
* :cmake:function:`qi_add_test` can now handle test script as target instead of binary.

Python
+++++++

* Added ``qisrc.sync`` for synchronizing a worktree with a manifest
* Added ``qisrc.review`` for configuring a project to use gerrit
* Added ``qibuild.deploy`` to handle deploying code to a remote target
* Added ``qibuild.gdb`` to allow stripping debug symbols out of the libraries
* Added ``qibuild.ui`` for tools to interact with the user
* Added ``qixml`` to help XML parsing, get rid of ``lxml`` dependency
* Added ``qisrc.git.get_repo_root``
* Added ``qisrc.git.is_submodule``
* Renamed `qisrc.worktree.worktree_open` to ``qisrc.worktree.open_worktree``
* Renamed ``qibuild.worktree`` to ``qisrc.worktree``
* ``qibuild.config.QiBuildConfig.read``: learned ``create_if_missing`` option
* ``install-qibuild.sh`` now installs ``qibuild`` scripts in ``~/.local/bin``
* ``qisrc.git.Git.call`` fix using ``quiet=True`` with ``raises=False``
* ``qisrc.git.Git.get_current_branch`` : return None when in 'detached HEAD' state
* ``qibuild.command.call`` learned ``quiet`` option
* Usage of ``qibuild.log`` and ``logging.py`` has been deprecated, use ``qibuild.ui`` instead
* ``toc.test_project`` has been removed, use ``qibuild.ctest`` instead
* ``toc.resolve_deps`` has been removed, use ``qibuild.cmdparse.deps_from_args`` instead
* ``qisrc.git.get_current_branch`` : return None when in 'detached HEAD' state
* Add ``qixml`` to help XML parsing, get rid of ``lxml`` dependency
* ``qibuild.command.call`` add ``quiet`` option
* Remove usage of ``qibuild.log`` and ``logging.py`` to display nice colorized messages
  to the console, use ``qibuild.ui`` module.
* Refactoring of the whole module ``qibuild.archive``:

  * Non-compatible APIs
  * Removed APIs:

    * ``qibuild.archive.extracted_name``
    * ``qibuild.archive.archive_name``
    * ``qibuild.archive.extract_tar``: use ``qibuild.archive.extract`` instead
    * ``qibuild.archive.extract_zip``: use ``qibuild.archive.extract`` instead
    * ``qibuild.archive.zip``: use ``qibuild.archive.compress`` instead
    * ``qibuild.archive.zip_unix``: use ``qibuild.archive.compress`` instead
    * ``qibuild.archive.zip_win``: use ``qibuild.archive.compress`` instead
  * New APIs:

    * ``qibuild.archive.compress``: include ``algo`` option, which is set
      to  ``zip`` when unspecified
    * ``qibuild.archive.guess_algo``: guessing the compression method
      from the archive extension

  * Updated APIs:

    * ``qibuild.archive.extract``:

      * support for the ``topdir`` option has been removed
      * add ``algo`` option, when unspecified ``algo`` is set to ``zip`` on all platform

* Added ``qibuild.cmake.modules`` to handle CMake module generation
* Renamed ``qibuild.cmdparse`` to ``qibuild.script``
* ``qibuild.cmdparse`` now centralize the parsing of qibuild actions arguments
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
* ``qibuild config --wizard:``: fix generator discovery for cmake 2.8.6 under windows
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

* add ``qibuild.sh.change_cwd``
* add ``qibuild.sh.is_executable_binary``
* ``qisrc.git`` : rewrite
* ``qibuild.cmdparse.run_action`` : allow adding ``--quiet-commands``
* add ``qitoolchain.binary_package`` : provide functions to open binary
  packages
* add ``qitoolchain.binary_package.core`` : abstract class for binary
  package provided by standard Linux distribution
* add ``qitoolchain.binary_package.gentoo`` : binary package class for
  *Gentoo* package (does not depends on *portage*)
* add ``qitoolchain.binary_package.gentoo_portage`` : binary package
  class for *Gentoo* package taking benefit from *portage*
* ``qibuild.archive.extract`` , :py:func: `qibuild.archive.extract_zip` ,
  ``qibuild.archive.extract_tar`` : add ``quiet`` keyword argument
  allowing non-verbose extraction
* ``qibuild.archive.extract_tar`` : fix archive name guessing
* ``qibuild.interact`` : add ``get_editor`` function

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
