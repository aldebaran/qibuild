qibuild TODO
=============

Below you can find a list of tasks that are not worth putting in a bug tracker.

Mostly because they involve some refactoring, or because they would cause
so many changes we are not sure if/when we will tackle them.

Feel free to add your own ideas here.

CMake
-----

qi_stage_lib/qi_use_lib
++++++++++++++++++++++++

* Handle package versions?
* Use new CMake 2.8.11 features
* avoid using the cache for global variables and use global properties instead

Factorize qi_create_test() and qi_create_perf_test()
+++++++++++++++++++++++++++++++++++++++++++++++++++++

It maybe a good idea to remove the compatibility with
pure cmake tests.

Instead, only use qi_create_test and generate custom
files instead (thus we no longer have to parse cmake-generated
cmake code)

It became easier to write code like this

.. code-block:: cmake

  qi_create_test(... NIGHTLY)
  qi_create_test(.... PERF)

Introduce options like ``WITH_TESTS``, ``WITH_PERF_TESTS``
instead of having to deal with ``BUILD_TESTS`` and ``enable_testing()``

Use a build 'prefix'
++++++++++++++++++++

``qibuild`` does lots of black magic so that you can find dependencies and headers paths
from the sources and build dir of your project, without using the "global cmake registry"
or any other tricks.

However:

* this means you can have problems with your headers install rules and not see them
* this also means you cannot easily depend of a project not using qibuild (even if it uses CMake),
  or a project using autotools

The solution is simple: After building a dependency, install it to ``QI_WOKTREE/root``  and
just set ``CMAKE_INSTALL_PREFIX`` to ``QI_WOKTREE/root``

This will work with any build system, (provided they have correct install rules), and will
force people to have correct install rules.

Make it easier to use 3rd party cmake module
++++++++++++++++++++++++++++++++++++++++++++++


Say you find a `foo-config.cmake` somewhere... If you try to do

.. code-block:: cmake

  find_package(FOO)

  qi_create_bin(bar)

  qi_use_lib(bar FOO)

This may or may not work: it depends of what the `foo-config.cmake` does:
`qi_use_lib` , `qi_stage_lib` expects some variables (`FOO_INCLUDE_DIRS`, `FOO_LIBRARIES`) to be
in the cache

It may be cleaner to add a `qi_export` function

.. code-block:: cmake

  find_package(FOO)

  # works out of the box if foo follows CMake conventions
  qi_export(foo)


  # can specify alternative variable names (here the case is wrong)
  qi_export(foo
    LIBRARIES ${Foo_LIBRARY}
  )

Make it easier to stage and use header-only libraries
+++++++++++++++++++++++++++++++++++++++++++++++++++++

Basically, go from

.. code-block:: cmake

  find_package(EIGEN3)
  include_directories(${EIGEN3_INCLUDE_DIRS})
  include_directories("include")
  qi_stage_header_only_lib(foo DEPENDS EIGEN3)


To

.. code-block:: cmake

  qi_create_header_only_lib(foo ${public_headers})
  qi_use_lib(foo EIGEN3)
  qi_stage_lib(foo)


where ``foo`` is a header-only library depending on
``Eigen3``





Command line
------------

* add group for every action parser, or only display the options
  specific to the given action when using `qibuild <action> --help`

* add a "path" type in argparse so that (on Windows at least) we:

  * always convert to lower case
  * check for forbidden characters

* make output more consistent (use the same color for the same thing
  everywhere for starters), this probably means extending the ``qisys.ui`` API

* make ``qisrc init`` works with a local directory containing a worktree (maybe
  ``qisrc clone``). but init seems better. "Are you a manifest git repo? No?
  So clone all."

* make git dependency optional

qibuild
-------

* Use 3 components: build, runtime, test (ala maven)

* add --reverse-deps

* `qibuild config` should list the available build profiles

* fix linker problems when using toolchain and third party libraries on mac

* fix XCode support and other "multi-configuration" IDE by having
  two SDK_DIRS (one debug, one release) in the same build dir

* handle custom build dir

* handle custom sdk dir?

* qibuild deploy: fix gdb config files generation

* get rid of qibuild test ``--slow``, this makes no sense: the
  list of tests and wether they are nightly or not is managed from cmake

* add qibuild test --failed

* add ``qibuild find -z`` to look in every build dir

* Better integration with QtCreator:

  * Write our own plugin to avoid the "CMakeList" pop-up (it only re-runs
    CMake to generate an XML code-blocks file, that is then re-parsed
    by QtCreator)
  * Match qitoolchain configs with QtCreator's kits
  * Automatically configure tests when they take arguments

qisrc
-----

* remove ``qisrc snapshot --manifest``

* fix ``qisrc manifest`` API

* qisrc sync:

  * implement ``--rebase-devel``

* find a better ``qisrc manifest`` API. Do we really need to support
  several manifests in the same worktree?

* mirroring qisrc manifests. (Same repos, same review, but an other
  "base URL")

* use ``--depth``  option when cloning. May speed up the initial
  clone

qitoolchain
-----------

Add metadata in the qitoolchain package format
++++++++++++++++++++++++++++++++++++++++++++++

At the very least ``name``, ``version`` and ``arch``.

Tracking dependencies may be a good idea, too.

This will allow to replace ``qitoolchain add-package foo foo.zip`` with
``qitoolchain add-package foo.zip`` with makes much more sense

Also : use XML for persistent storage of toolchain packages and add override
config files to track the packages the user manually adds or removes

This will solve the bug ``qitoolchain remove-package boost; qitoolchain update`` that
makes boost reappear in the toolchain.


qidoc
-----


Python
-------

Port to Python3
+++++++++++++++++

It's the future ! We already removed compatibility with ``Python 2.6``, and
``python3`` is now the default version on most linux distros.

Renames
++++++++

* XMLParser.xml_elem() -> dump()
* XMLParser._write_foo()  -> _dump_foo()

* rewrite qibuild.config using XMLParser

* rename qibuild.config -> qibuild.xml_config?

* choose between destdir and dest_dir

* qisrc.status.check_state(project, untracked) -> qisrc.status.check_state(project, untracked=False)

* what we call "zombies" in the implementation of ``qibuild test`` are actually orphans
  (see http://en.wikipedia.org/wiki/Orphan_process), so we should fix the
  code accordingly. Plus this means we can write a ``kill_orphans`` method :)

tests
+++++

* Document ``pytest`` fixtures: we have tons of them, and some of them are
  very magic

* Replace qibuild_action("configure") with a nicer syntax:

  * qibuild_action.call("configure")?
  * qibuild_action.configure("...")?

* fix running automatic tests on mac

misc
++++

* parser.get_* functions should be usable with ``**kwargs`` too::

    def get_worktree(args=None, **kwargs):
      options = dict()
      if args:
        options = vars(args[0])
      else:
        options = kwargs

* ``qisrc.parser.get_projects(worktree, args)`` -> ``qisrc.parser.get_projects(args)``
  (just get the worktree from the args)


* replace ``qisys.interact.ask_choice``
  Instead of a ``return_int`` option, use something like:
  ``ask_choice(message, choices, display_fun=None, allow_none=False)``

  ``display_fun`` will be called on each choice to display them
  to the user, returning either an element from the choices
  list, or None if the user did not enter anything and ``allow_none`` is True

* Use same API as ``shutil`` in ``qisys.sh`` and ``qisys.archive``:

  * qisys.command.find -> qisys.command.which

  * qisys.command.archive -> http://docs.python.org/3/library/shutil.html#archiving-operations


* Add convenience methods: ``CMakeBuilder.test()``, ``project.test()`` to wrap
  ``qibuild.ctest.run_tests``

qibuild2 leftovers cleanup
++++++++++++++++++++++++++

* remove qitoolchain.Toolchain.get

* remove qibuild.configstore, use XML for toolchain
  storage
