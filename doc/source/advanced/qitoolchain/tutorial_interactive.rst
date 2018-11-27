.. _qitoolchain-tutorial_interactive:

Creating conan packages with qitoolchain
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

Creating conan package with qibuild interactivity
-------------------------------------------------

Let's assume we will need a package for qitoolchain with shared boost inside.

.. code-block:: console

    qitoolchain convert-package --conan --name=boost --version=1.68.0 .
    Switch to interactive mode
    :: Which conan library do you want to add? (True)
    > boost/1.68.0@conan/stable
    :: Do you want it to be shared (highly recommended)? (Y/n)
    > yes

In this way qitoolchain will detected that the conanbuildinfo.json is missing and
will ask you for some informations about what you want to build.

| The first thing is the name of the channel, something like: ``boost/1.68.0@conan/stable``.
| The second thing is if you want the shared version of the library (Yes by default).
| Then it will write a conanfile in a tmp directory, build it and pass it the to rest of the process.

Here we are. A new package is now available and you can add it to you toolchain feed:

.. code-block:: console

    qitoolchain add-package -t linux64 boost-Linux-x86_64-1.68-0.zip
