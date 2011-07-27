## Copyright (C) 2011 Aldebaran Robotics

#! qiBuild Install
# ================
#
# == General overview ==
#
# === Components ===
# The various qi_install_* function deals with the components and respect the
# SDK layout for you.
#
# They also help you producing 'runtime' packages (containing just what is necessary
# to run your software), or 'developpement' packages (containing everything in the
# runtime package, plus all that is necessary to use your : headers, library,
# cmake config files, et al.)
#
# === Examples ===
#
# We know that this is not at all easy to understand, so here are some examples
#
# * With headers in several different folders  (a bit like autotools):
#
# ----
# sources:                      destination
#   foo                          include
#   |__ include                  |__ foo
#       |__ foo.h                       |__ foo.h
#       |__ bar.h                       |__ bar.h
#   config.h (generated)                |__ config.h
# ----
#
# use:
#
# [source, cmake]
# ----
# qi_install_header(foo/include/foo.h
#                   foo/include/bar.h
#                   ${CMAKE_BUILD_DIR}/config.h
#                   SUBFOLDER foo)
# ----
#
# qi_install_header will set DESTINATION "include" for you,
# but you need 'SUBFOLDER foo' argument to tell CMake to install files
# to include/foo, regardless their original path.
# This is default CMake behavior.
#
#   * With headers following the exact same hierarchy in the source tree and when
#     installed  (a bit like boost)
#
# ----
# sources                         destination
#   libfoo                        include
#   |__ foo                       |__ foo
#       |__ foo.h                     |__ foo.h
#       bar                           bar
#       |__ bar.h                     |__ bar.h
#           baz                           baz
#           |__ baz.h                     |__ baz.h
# ----
#
# use:
#
# [source, cmake]
# ----
# qi_install_header(foo/foo.h
#                   bar/bar.h
#                   bar/baz/baz.h
#                   KEEP_RELATIVE_PATHS)
# ----
#
# qi_install_header will set DESTINATION "include" for you, and you do not need
# SUBFOLDER because KEEP_RELATIVE_PATHS is set.
#
# === Runtime versus development installation ===
#
# Here are the components that will be used during a runtime install:
#
# ----
# component          function                 destination
#
# "binary"          qi_create_bin             bin/
# "lib"             qi_create_lib(SHARED )    lib/ on UNIX, bin/ on windows
# "conf"            qi_install_conf           etc/
# "data"            qi_install_data           share/
# "doc"             qi_install_doc            share/doc
# ----
#
# Note that qi_create_bin and qi_create_lib create the install rules for you by default.
# If you don't what the executable to be installed (because it's just a test, for instance, you can use:
# qi_create_bin(foo NO_INSTALL)
#
# If you want to install an executable that is NOT the result of a compilation (for instance a script),
# you can use qi_install_program()
#
#
#
#
# When doing a normal install, you will get the previous componet, plus
# the following ones:
#
# ----
# component          function                  destination
#
# "static-lib",      qi_create_lib(STATIC)     lib/
# "cmake"            qi_stage_lib(             share/cmake/modules/
# "header"           qi_install_header         include/
# ----
#
#
# If you want to install something in your devel install that does not fit
# in these components (say, an example), you can use the generic
# qi_install() function
#
# For instance:
#
# [source, cmake]
# ----
# qi_install(foo_example bar_examples DESTINATION examples KEEP_RELATIVE_PATHS)
# ----
#
# will give you:
#
# ----
#   sources:                      destination
#
#                                  examples
#   foo_example                    |__ foo_example
#   |__ CMakeLists                    |__ CMakeLists
#   |__ foo.cpp                       |__ foo.cpp
#   bar_example                       bar_example
#   |__ CMakeLists                    |__ CMakeLists
#   |__ bar.cpp                       |__ bar.cpp
# ----
#
# Also, to install a README at the root of your package you could do:
#
# ----
#   qi_install(doc/README DESTINATION ".")
# ----
#
# Since no component as been given, this files won't be in the runtime install.
#
#
# === About plugins ===
#
# A plugin is a library that is supposed to be opened by the executable, but is not necessary right next to
# the executable.
# In this case you must use:
#
#
# [source, cmake]
# ----
# qi_create_lib(SHARED foo SUBFOLDER bar)
# ----
#
# you will end up with
#
# lib/bar/libfoo.{so,dylib}  on unix
#
# and
#
#  lib/bar/foo.dll on windows
#
# (Reminder: without SUBFOLDER argument, dll will end in bin/, to that whatever
# executable that needs the foo.dll can run out of the box)
#
# You can then use qi::path and qi::os functions to do something like:
#
# [source, cpp]
# ----
# const std::string foo_lib = qi::path::findLib(bar/foo);
# void* handle = qi::os::dlopen(foo_lib);
# // ... do something using qi::os::dlsym(handle ...);
# qi::os::dlclose(handle);
# ----
#
#
# === About configuration files ===
#
# If you have a configuration file named +foo.cfg+ which is put into version control in
# your source tree, you may way to use something like:
#
#
# [source, cmake]
# ----
# configure_file(foo.cfg ${QI_SDK_DIR}/${QI_SDK_CONF}/foo/foo.cfg)
# qi_install_conf(foo.cfg SUBFOLDER foo)
# ----
#
# This way you can be sure the layout for foo executable and foo.cfg is always the same
# whereas foo has just been compiled into a build directory, or foo is now installed.
#
# ----
# <prefix>
# |__ bin
#     |__ foo
# |__ etc
#     |__ foo
#         |__ foo.cfg
# ----
#
#
# In both cases using something like:
#
#
# [source, cpp]
# ----
# std::string foo_cfg = qi::findConf(foo/foo.cfg);
# // ... do something with foo.cfg
# ----
#
#
# will always work
#
# === Special syntax features ===
#
# ==== Support of glob and directories ===
# Please not that on top of this, you can use directories, globbing expressions
# and list of files as arguments on all qi_install_* functions.
#
# For instance:
# qi_install(foo/bar/ *.txt spam.cfg eggs.cfg DESTINATION "prefix")
# will install:
#  - directory foo/bar to "prefix/bar"
#  - every .txt file in current directory to "prefix"
#  - the spam and eggs cfg file to "prefix"
#
# ==== "IF" keyword ====
# instead of using
#
# [source, cmake]
# ----
# if(FOO)
#    qi_install(.... )
# endif()
#----
#
# you can use:
#
# [source, cmake]
# ----
#    qi_install(.... IF FOO)
# ----
#


#! Generic install function.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
function(qi_install)
  _qi_install_internal(${ARGN})
endfunction()

#! Install application headers.
# The destination will be <prefix>/include/
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
function(qi_install_header)
  _qi_install_internal(${ARGN} COMPONENT header DESTINATION ${QI_SDK_INCLUDE})
endfunction()



#! Install application data.
# The destination will be: <prefix>/share/
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_data)
  _qi_install_internal(${ARGN} COMPONENT data  DESTINATION ${QI_SDK_SHARE})
endfunction()

#! Install application doc.
# The destination will be: <prefix>/share/doc/
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_doc)
  _qi_install_internal(${ARGN} COMPONENT doc   DESTINATION ${QI_SDK_DOC})
endfunction()


#! Install application configuration files.
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_conf)
  _qi_install_internal(${ARGN} COMPONENT conf  DESTINATION ${QI_SDK_CONF})
endfunction()

#! Install CMake module files.
# The destination will be: <prefix>/share/cmake/
#
# \argn:                 A list of files : directories and globs on files are accepted.
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
# \flag: KEEP_RELATIVE_PATHS  If true, relative paths will be preserved during installation.
#                        (False by default because this is NOT the standard CMake
#                         behavior)
#
function(qi_install_cmake)
  _qi_install_internal(${ARGN} COMPONENT cmake DESTINATION ${QI_SDK_CMAKE})
endfunction()


#! install a target, that could be a program or a library.
#
# \argn:                 A list of targets to install
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
function(qi_install_target)
  cmake_parse_arguments(ARG "" "IF;SUBFOLDER" "" ${ARGN})

  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (NOT _doit)
    return()
  endif()

  if(ARG_SUBFOLDER)
    set(_dll_output ${QI_SDK_LIB}/${ARG_SUBFOLDER})
  else()
    set(_dll_output ${QI_SDK_BIN})
  endif()

  if(WIN32)
    set(_runtime_output ${_dll_output})
  else()
    set(_runtime_output ${QI_SDK_BIN}/${ARG_SUBFOLDER})
  endif()

  foreach (name ${ARG_UNPARSED_ARGUMENTS})
    install(TARGETS "${name}"
            RUNTIME COMPONENT binary     DESTINATION ${_runtime_output}
            LIBRARY COMPONENT lib        DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER}
      PUBLIC_HEADER COMPONENT header     DESTINATION ${QI_SDK_INCLUDE}/${ARG_SUBFOLDER}
           RESOURCE COMPONENT data       DESTINATION ${QI_SDK_SHARE}/${name}/${ARG_SUBFOLDER}
            ARCHIVE COMPONENT static-lib DESTINATION ${QI_SDK_LIB}/${ARG_SUBFOLDER})
  endforeach()
endfunction()

#! install program (mostly script or user provided program). Do not use this function
# to install a library or a program built by your project, prefer using qi_install_target.
#
# \argn:                 A list of programs to install
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
function(qi_install_program)
  cmake_parse_arguments(ARG "" "IF;SUBFOLDER" "" ${ARGN})

  if (NOT "${ARG_IF}" STREQUAL "")
    set(_doit TRUE)
  else()
    #I must say... lol cmake, but NOT NOT TRUE is not valid!!
    if (${ARG_IF})
    else()
      set(_doit TRUE)
    endif()
  endif()
  if (NOT _doit)
    return()
  endif()

  foreach(name ${ARG_UNPARSED_ARGUMENTS})
    #TODO: what should be the real source here?
    install(PROGRAMS    "${QI_SDK_DIR}/${QI_SDK_BIN}/${ARG_SUBFOLDER}/${name}"
            COMPONENT   binary
            DESTINATION "${QI_SDK_BIN}/${ARG_SUBFOLDER}")
  endforeach()
endfunction()


#! install external library. Do not use this function
# to install a library or a program built by your project,
# prefer using qi_install_target.
#
# \argn:                 A list of libraries to install
# \param: SUBFOLDER      An optional subfolder in which to put the files.
# \param: IF             Condition that should be verified for the install rules
#                        to be active for example (IF WITH_ZEROMQ)
function(qi_install_library)
  _qi_install_internal(${ARGN} COMPONENT lib DESTINATION ${QI_SDK_LIB})
endfunction()
