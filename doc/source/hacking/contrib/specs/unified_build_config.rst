Unified build configuration
============================

The problems
------------

* Suppose you have a build folder named ``atom-nao``. How do
  you know whether it is the ``atom-nao`` toolchain
  (containing pre-compiled binaries using the ``nao`` profile),
  or the ``atom`` toolchain, with the ``nao`` profile ?

* You must deploy your code using ``--release`` because it's
  just too slow to run properly otherwise. But when
  you want to debug your own module, you do something like:
  ``qibuild configure``, ``qibuild make``, ``qibuild deploy -s``.

  This is annoying because you have to re-build everything in debug
  even though you are just deploying one project in debug.

The solution
-------------

Introduce the concept of ``build-config``. It is given
a unique string across all worktrees, and contains the following
info:

* build type (debug, release)
* toolchain
* list of build profiles.

They are stored in ``~/.config/qi/qibuild.xml`` thusly:

.. code-block:: xml

    <qibuild>
      <configs>
        <config name="nao">
          <build_type>release</build_type>
          <toolchain>atom<toolchain/>
          <profiles>
            <profile>nao</profile>
          </profiles>
        </config>
      </configs>
    </qibuild>

The build folder is named after the config.
In this case ``build-nao``. The command line to use
the ``nao`` config is ``-c nao``.

The ``-p, --profile`` option is removed.

When using ``-c atom`` you can use ``--debug -s`` to
only compile a project in debug, and it will use the same
build directory.

(There is no danger of using the same build directory for debug and
release, even on Visual Studio)

When we have binary packages compiled with the nao profile,
it's easy to use it in the 'atom-nao' toolchain by changing
``qibuild.xml`` to have

.. code-block:: xml

    <config name="nao">
      <toolchain>nao-atom</toolchain>
      <profiles>
        <profile>nao</profile>
      </profiles>
      ...
    </config>

Bonus: you can keep your build folders !
