.. _qibuild-shared-libs:

Managing shared libraries
=========================

Reminder: we want to the hello executable to find the world library when it is
run.

We have two cases to deal with:

* When we’ve just compiled the hello executable

* When we’ve made a package containing hello and world.

Linux and .so
-------------

This is by far the easiest case!

CMake already does The Right Thing when hello has just been compiled.

It just strips the RPATH during installation.

This is fixed by calling:

.. code-block:: cmake

  set_target_properties("${name}"
    PROPERTIES
      INSTALL_RPATH "\$ORIGIN/../lib"
  )

Windows and .dll
----------------

Windows is just a bit harder. The hello.exe will be happy as soon as the
world.dll is just next to it.

Since CMake knows about the dependencies of the hello project, it is easy to
parse the list of hello dependencies, look for which of them are dynamic
libraries, and copy them next to the executable in a "post build" command.

This is achieved by running a cmake script called. post-copy-dlls.cmake. It is
was generated in the build dir of the hello and then called with correct
arguments.

More specifically, the "post-copy-dlls.cmake+ we create is always the same

Here is what it looks like

.. code-block:: cmake

  set(_to_copy)

  foreach(_dep ${PROJECT_DEPENDS})
    list(APPEND _to_copy ${_dep}_LIBRARIES)
  endforeach()

  file(COPY ${_in_dlls} DESTINATION ${QI_SDK_DIR}/${QI_SDK_LIB}/${BUILD_TYPE})

We then add a post-build rule :

.. code-block:: cmake

  add_custom_command(TARGET ${name} POST_BUILD
    COMMAND
      ${CMAKE_COMMAND}
      -DBUILD_TYPE=${CMAKE_CFG_INTDIR}
      -DPROJECT=${_U_name}
      -P ${CMAKE_BINARY_DIR}/post-copy-dlls.cmake
      ${CMAKE_BINARY_DIR}

CMAKE_CFG_INTDIR is something like $(OutDir), a variable that is expanded by
the native tool. In the case of visual studio, it’s the name of the current
build configuration.

Remember, CMake configures one sln that must be used in several build
configurations.

So for instance, we will call::

  c:\cmake\cmake.exe -DBUILD_TYPE=Debug -DPROJECT=HELLO -P hello\build\post-copy-dlls.cmake hello\build

When you run cmake -P with two arguements, the last one is the path to the cache.

This is how we can find every variable we need, like HELLO_DEPENDS and
WORLD_LIBRARIES.

The last two variables we need (PROJECT and BUILD_TYPE), are directly set on
the command line.

Nice, isn’t it?

MacOSx and .dylib
-----------------

MacOSx is tricky. In fact we still do not have a working implementation for the
moment.

You may still need to tweak DYLD_LIBRARY_PATH from time to time.

If libworld.dylib has NOT been installed, everything works. CMake gently set
the install_name_too so that hello is able to find
/path/to/src/world/build/sdk/lib.

But, when libworld.dylib is installed, hello cannot find libworld.dylib, even
though the linker knows the full path of libworld.dylib.

(this is different from the way ld works on linux)

This is how it works today:

* We tell cmake to always set install_name to @executable_path/../lib

* In the post-build rule of hello, we look for hello dependencies, and copy the
  .dlylib, so that we can have::

    path/to/src/hello/build/sdk/bin/hello
    path/to/src/hello/build/sdk/lib/libworld.dylib

(this is exactly the same trick as for the post-copy-dlls.cmake file.)

The only problem left is with third-party libraries: we did not know what
install name tool they have chosen, nor if they used the correct linker flags....

We could try to run install_name_tool -change ... on the third party libraries,
but we have to know the original install name in order to change it :/

