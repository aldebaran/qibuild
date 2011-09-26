Using a cross toolchain
=======================

.. FIXME: This probably not longer works:/
   Probably the best way would be
   qibuild use-toolchain cross-geode /path/to/ctc.tar.gz
   qibuild use-toolchain linux32     /path/to/sdk.tar.gz

Using a cross toolchain is not very different from using a toolchain.

Here is what Aldebaran's cross toolchains look like

There are three main parts:

* A directory where to find the cross-compiler (called cross),

* A directory containing a root file system similar to the one present on the
  target (called sysroot)

* A tooclhain.cmake file.

Here is what the file hiearchy looks like::

  ctc
  |__ cross
      | ....
      | Files used by the cross-compiler
  |__ sysroot
      | ...
      | Similar to what is found on the target.
      |__
         |__ usr/
         |   |__ lib/
             |__  share/
         |__ lib/
  toolchain.cmake

The purpose of toolchain.cmake file is to tell cmake where the cross-compiler
is (we do not want to use the host compiler by definition), and to tell cmake
that it should not look for libraries in the host system (say, find boost in
/usr/include/boost), but in the syroot of the cross toolchain (ie we want to
find boost in ctc/sysroot/usr/include/boost)

Basically, the toolchain_file looks like this:

.. code-block:: cmake

  set(CMAKE_FIND_ROOT_PATH  "ctc/sysroot")

  # Force the compiler
  CMAKE_FORCE_C_COMPILER(  "ctc/sysroot/bin/i686-pc-linux-gnu-gcc" GNU)
  CMAKE_FORCE_CXX_COMPILER("ctc/sysroot/bin/i686-pc-linux-gnu-g++" GNU)

  #  Custom flags for the target:
  set(CMAKE_C_FLAGS "--sysroot ctc/sysroot -march=... )

So how do you configure qibuild to use the cross toolchain ?

Here's what you should do :

Create a .qi/build-cross.cfg looking like::

  [general]
  cmake.flags = CMAKE_TOOLCHAIN_FILE=/path/to/ctc/toolchain.cmake

Then, you can run::

  qibuild configure -c cross

In your project. You will be using the .qi/build-cross.cfg, and path the
ctc/toolchain.cmake file to cmake when configuring your project, and that’s all
there is to do ...

