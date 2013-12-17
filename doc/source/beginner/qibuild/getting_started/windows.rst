Getting started with qibuild on Windows
=======================================

Install CMake
-------------

``qibuild`` uses ``CMake``. Get the latest version from ``http://cmake.org``,
and make sure that ``CMake`` is in your ``PATH``

It also means that ``qibuild`` is compatible with every compiler supported by
``CMake``.

Install a compiler
--------------------

On windows, the best supported ways to use qibuild is with

* Visual Studio
* or QtCreator  (using mingw)


First run
----------

You should run

.. code-block:: console

   $ qibuild config --wizard

The first time you run qibuild and then answer the questions.

A file will be generated in ``~/.config/qi/qibuild.xml``.
It is shared by all the worktrees you will create.

You will ask to choose a CMake generator.
The generator you want to use depends on how you wish to use qibuild
Configuring qiBuild

Note that you can run ``qibuild config`` to get a look at your current
settings, and change them by editing the xml files, or re-running ``qibuild
config --wizard``


Building with Visual Studio
---------------------------

You will have to make sure CMake uses the proper generator for qiBuild to work
with Visual Studio.

Note when using Aldebaran packages, 64bits support is not available. You can
still use Visual Studio on a 64bits machines to build and run 32 bits executable
with a 32bist SDK, though.

Here is what a complete ``~/.config/.qi/qibuild.xml`` would look like to use Visual Studio 2010

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <cmake generator = "Visual Studio 10" />
    </defaults>
  </qibuild>


Then just open the ``.sln`` that will be generated in the build directory.


If you want, you can also use an other generator than Visual Studio.
You may build faster using an other generator, at the cost of not having an IDE
to browse your source code.

If you choose to do so, you should either:

* Run qibuild from the Visual Studio command prompt

* Or specify a ``.bat`` file to be ran by qibuild, like this


.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <env bat_file="c:\Program Files\Microsoft Visual Studio 10\VC\vcvarsall.bat" />
    </defaults>
  </qibuild>

(the location of the ``.bat`` file depends on your setup)

* Then, you can choose an other generator such as ``NMake Makefiles``, ``Jom`` or
  ``Ninja``

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <cmake generator="Ninja" />
   </defaults>
  </qibuild>


Configuring qiBuild for QtCreator
---------------------------------

The preferred way to use qibuild on Windows is with Visual Studio, and please
note that Aldebaran does not provide a C++ SDK for mingw.

But, if you do not want to use Visual Studio, you can still use qibuild
with QtCreator and the mingw package that comes with it.

* Get the latest qtcreator and install it. (you only need the qtcreator
  package, no need for the full-fledged Qt SDK)

* Add the MinGW’s path to your %PATH% so that QtCreator can find mingw32-make
  without running qmake

* Tell qibuild to use "MinGW Makefiles"

Here is what a complete ``.config/.qi/qibuild.xml`` would look like to use MinGW with QtCreator

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <env path="C:\QtSDK\mingw\bin" />
      <cmake general="MinGW Makefiles" />
    </defaults>
  </qibuild>


.. warning:: qibuild never modify os.environ globally, so the executable you
   just built won't run unless you have mingw's DLLs in your PATH,
   but it should run from QtCreator without problems


Please read the ``qibuild-qtcreator`` section to learn how to build from
QtCreator.

Configuring qiBuild for MinGW with Msys
---------------------------------------

You will have to do several things for qibuild to work with MinGW.

* Set PATH properly so that make.exe and gcc.exe are found

* Make sure CMake uses the correct generator

Here’s what a complete ``.config/qi/qibuild.xml`` would look like to use MinGW

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <env path="C:\Mingw\bin;C:\MinGW\msys\1.0\bin;" />
      <cmake generator = "Unix Makefiles" />
    </defaults>
  </qibuild>

.. note:: here you have to setup a complete msys environnement before being
   able to use qibuild.

Using JOM
----------

Get the JOM package from here: `ftp://ftp.qt.nokia.com/jom <ftp://ftp.qt.nokia.com/jom/>`_
and extract it, for instance in ``C:\Jom109``

Then, add jom to you path and use **MinGW Makefiles JOM** generator:

For instance:

.. code-block:: xml

  <qibuild version="1">
    <defaults>
      <env
        bat_file="c:\Program Files\Microsoft Visual Studio 9.0\VC\vcvarsall.bat" />
        path="C:\Jom109"
      />
      <cmake generator = "NMake Makefiles JOM" />
    </defaults>
  </qibuild>


Using Ninja
-----------

`Ninja <http://martine.github.com/ninja/>`_ is a small build system with a focus on speed.

``Ninja`` is supported by ``CMake`` since 2.8.10, and by ``QtCreator``
since 2.6.1

Support for ``Ninja`` is still experimental, but by using it
you should experience faster compilations, especially during incremental
builds.

First, get ninja from github and compile it:

.. code-block:: console

    $ git clone git://github.com/martine/ninja.git
    $ cd ninja
    $ python ./bootstrap.py

.. note:: On Windows, you need to run this form the Visual Studio command
    prompt so that cl.exe can be found, or, if you are using mingw,
    from a mingw command prompt

Then make sure that ``ninja`` is in your PATH.

To use it, edit ``.config/qi/qibuild.xml`` to look like:

.. code-block:: xml

    <qibuild version="1">
      <build />
      <defaults>
        <cmake generator="Ninja" />
      </defaults>
    </qibuild>

Or just re-run ``qibuild config --wizard``
