.. _qibuild-qtcreator:

Building with qibuild and QtCreator
===================================


The only thing to remember is that you should not let QtCreator call CMake by
itself the first time.

Use ``qibuild configure`` then ``qibuild make`` to be sure everything works
fine.

Then open the root CMakeLists in qtcreator.

You will be prompted to use a build directory:

.. image:: /pics/qtcreator-build-location.png

.. warning:: Do not use the default one proposed by QtCreator,
   choose the one that was created by qiBuild


QtCreator will read the settings from the existing build directory, so
everything should work fine.

Remember to use the same CMake generator in QtCreator and in your configuration
file, if qtcreator asks you to choose one.

Note: If QtCreator does not ask you for a build directory, one way to force it
do to so is to delete the ``CMakeLists.txt.user`` file.

.. image:: /pics/qtcreator-hello.png
