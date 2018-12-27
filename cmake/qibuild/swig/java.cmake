## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! CMake wrapper for swig / Java
# ==============================

#!
# Create a java wrapping of the C/C++ library
#
# .. warning:: The ``name`` must match the name declared in ``interface_file``
#     for instance, if ``name`` equals Foo, `Foo.i` must contain:
#     ``%module Foo``, and the generated library will be called 'libFoo.so'
#
#
# \arg:module_name the target name
# \arg:interface_file the swig interface file (extension is .i)
# \param:PACKAGE package name
# \param:OUTDIR swig output directory
# \flag:CPP whereas the lib is in C++
# \group:SRC The list of source files
# \group:DEPENDS The list of dependencies
#
function(qi_swig_wrap_java name interface_file)
  cmake_parse_arguments(ARG "CPP" "PACKAGE;OUTDIR" "SRC;DEPENDS" ${ARGN})
  message(STATUS "Swig/java: ${module_name}")

  find_package(Java REQUIRED QUIET)
  find_package(JNI REQUIRED)
  include_directories(${JNI_INCLUDE_DIRS})
  if(ARG_CPP)
    set_source_files_properties(${interface_file} PROPERTIES CPLUSPLUS ON)
  endif()
  if(ARG_PACKAGE)
    set_source_files_properties(${interface_file} PROPERTIES
      SWIG_FLAGS "-package;${ARG_PACKAGE}")
  endif()
  set(_srcs ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS})

  find_program(SWIG_EXECUTABLE swig)
  if(NOT SWIG_EXECUTABLE)
    qi_error("Could not find swig executable in PATH, please install it")
    return()
  endif()

  include("UseSWIG")
  include("UseJava")

  if(ARG_OUTDIR)
    set(_out_dir ${ARG_OUTDIR})
  else()
    set(_out_dir ${CMAKE_CURRENT_BINARY_DIR}/${name})
  endif()
  set(CMAKE_SWIG_OUTDIR ${_out_dir})

  ##
  # Deal with dependencies:
  set(_inc_dirs)
  foreach (_dep ${ARG_DEPENDS})
    find_package(${_dep} NO_MODULE QUIET)
    find_package(${_dep} REQUIRED)
    if(${_dep}_INCLUDE_DIR)
      _qi_list_append_path(_inc_dirs ${${_dep}_INCLUDE_DIR})
    endif()
    if(${_dep}_INCLUDE_DIRS)
      _qi_list_append_path(_inc_dirs ${${_dep}_INCLUDE_DIRS})
    endif()
  endforeach()

  foreach(_inc_dir ${_inc_dirs})
    include_directories(${_inc_dir})
  endforeach()

  find_package(JNI)
  include_directories(${JNI_INCLUDE_DIRS})
  # Since there is often a "lazy" include in the interface file:
  include_directories(${CMAKE_CURRENT_SOURCE_DIR})


  swig_add_module(${name} java ${interface_file} ${_srcs})

  ##
  # Deal with the newly created target

  # Store the target created by swig_add_module in a more friendly name:
  qi_use_lib(${name} ${ARG_DEPENDS})

  # Fix prefix and output directory
  set_target_properties(${name} PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY_DEBUG   "${QI_SDK_DIR}/${QI_SDK_LIB}"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${QI_SDK_DIR}/${QI_SDK_LIB}"
        RUNTIME_OUTPUT_DIRECTORY         "${QI_SDK_DIR}/${QI_SDK_LIB}"
        ARCHIVE_OUTPUT_DIRECTORY_DEBUG   "${QI_SDK_DIR}/${QI_SDK_LIB}"
        ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${QI_SDK_DIR}/${QI_SDK_LIB}"
        ARCHIVE_OUTPUT_DIRECTORY         "${QI_SDK_DIR}/${QI_SDK_LIB}"
        LIBRARY_OUTPUT_DIRECTORY_DEBUG   "${QI_SDK_DIR}/${QI_SDK_LIB}"
        LIBRARY_OUTPUT_DIRECTORY_RELEASE "${QI_SDK_DIR}/${QI_SDK_LIB}"
        LIBRARY_OUTPUT_DIRECTORY         "${QI_SDK_DIR}/${QI_SDK_LIB}"
        PREFIX "lib")

  # rpath fixes:
  if(UNIX)
    if(APPLE)
      set_target_properties("${name}"
        PROPERTIES
          INSTALL_NAME_DIR "@executable_path/../lib"
          BUILD_WITH_INSTALL_RPATH 1
      )
      set_target_properties("${name}"
        PROPERTIES
          INSTALL_RPATH "\$ORIGIN/../lib"
      )
    endif()
  endif()

  # TODO: compile the generated .java class and and the libFoo.so
  # in it.
  # NOT doable from cmake because there's no way to know
  # what .java files swig will generate before hand

endfunction()
