.. _qitoolchain-tutorial:

Managing conan packages with qitoolchain
========================================

What is conan
-------------

| Conan is a build tool written in Python to build and package C++ librairies.
| The Conan ecosystem gather a client tool and some servers repositories.
| Project built with Conan expose a python script to configure, build and package the project,
| these projects also store the package in a conan server.
|
| One of the usefull feature of conan, used here to build a qitoolchain package, is the conanfile.txt.
| This file list our dependencies and the build configuration of these packages.
| With one command we will be able to fetch the selected package or to rebuild them with our compiler.
| The output directory will contains all the data we will need to create a qitoolchain package.

Creating conanfile.txt and prepare package directory
----------------------------------------------------

Let's assume we will need a package for qitoolchain with shared boost inside.

.. code-block:: console

    [requires]
    boost/1.68.0@conan/stable

    [options]
    boost:shared=True

    [generators]
    json

    [imports]
    bin, *.dll -> ./bin
    lib, *.lib* -> ./lib
    lib, *.dylib* -> ./lib
    lib, *.so* -> ./lib
    include, * -> ./include


| We requires boost 1.68 from the official channel and we want it to be shared.
| qiToolchain needs a json file output from the generator and we declare the behavior of the importer.

.. code-block:: console

    conan install boost-conanfile.txt --build=missing --install-folder package

Converting package directory to qitoolchain package
---------------------------------------------------

So, we have a common directory structure with ./lib, ./bin, ./include.

.. code-block:: console

    qitoolchain convert-package --conan --name=boost --version=1.68.0 package/


Here we are. A new package is now available and you can add it to you toolchain feed:

.. code-block:: console

    qitoolchain add-package -t linux64 boost-Linux-x86_64-1.68.0.zip
