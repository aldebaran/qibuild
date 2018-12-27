## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.


include(CMakeParseArguments)
FIND_PACKAGE(SWIG REQUIRED)
INCLUDE(${SWIG_USE_FILE})

#! CMake wrapper for swig / Python
# ================================

#!
# Create a python wrapping of the C/C++ library
#
# .. warning:: The ``module_name`` must match the name declared in ``interface_file``
#     for instance, if ``module_name`` equals foo, `foo.i` must contain:
#     ``%module foo``
#
# For further details about the install locations, refer to :cmake:function:`qi_install_python`.
#
# \arg:module_name the target name
# \arg:interface_file the swig interface file (extension is .i)
# \group:SRC The list of source files
# \group:DEPENDS The list of dependencies
# \group:SUBFOLDER Subfolder where the module will be built. Used to add the wrapper to an existing package.
#
function(qi_swig_wrap_python module_name interface_file)
  message(STATUS "Swig/python: ${module_name}")
  cmake_parse_arguments(ARG "" "SUBFOLDER" "SRC;DEPENDS" ${ARGN})
  set(_srcs ${ARG_SRC} ${ARG_UNPARSED_ARGUMENTS})
  if (ARG_SUBFOLDER)
    set(_subfolder /${ARG_SUBFOLDER})
  endif()

  # we search for the SWIG_EXECUTABLE by yourself, because FindSWIG call find_file
  # but when we are cross-compiling and we want to use swig from the system
  # then CMAKE_FIND_ROOT_PATH prevent find_file from working.
  find_package(SWIG REQUIRED)
  include("UseSWIG")

  set_source_files_properties(${interface_file} PROPERTIES CPLUSPLUS ON)
  # tell swig that the generated module name is ${module_name}.py
  # without this property, it assumes that it is ${interface_file}.py
  # TODO: check that it is a correct way to do this and not a nifty hack
  set_source_files_properties(
    ${interface_file} PROPERTIES SWIG_MODULE_NAME "${module_name}")


  set(CMAKE_SWIG_OUTDIR ${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder})

  ##
  # Deal with dependencies:
  set(_inc_dirs)
  foreach (_dep ${ARG_DEPENDS})
    string(TOUPPER ${_dep} _U_dep)
    find_package(${_U_dep} NO_MODULE QUIET)
    find_package(${_U_dep} REQUIRED)
    if(${_U_dep}_INCLUDE_DIR)
      _qi_list_append_path(_inc_dirs ${${_U_dep}_INCLUDE_DIR})
    endif()
    if(${_U_dep}_INCLUDE_DIRS)
      _qi_list_append_path(_inc_dirs ${${_U_dep}_INCLUDE_DIRS})
    endif()
  endforeach()

  foreach(_inc_dir ${_inc_dirs})
    include_directories(${_inc_dir})
  endforeach()

  find_package(PYTHON)
  include_directories(${PYTHON_INCLUDE_DIRS})
  # Since there is often a "lazy" include in the interface file:
  include_directories(${CMAKE_CURRENT_SOURCE_DIR})

  swig_add_module(${module_name} python ${interface_file} ${_srcs})

  # When interface_file looks like "foo/foo.i", cmake 2.8.12 tries
  # to generate the fooPYTHON_wrap.cxx in build/foo/foo/ but fails
  # because it does not create the subdirectory
  get_filename_component(_interface_dir ${interface_file} DIRECTORY)
  file(MAKE_DIRECTORY ${CMAKE_CURRENT_BINARY_DIR}/${_interface_dir})

  ##
  # Deal with the newly created target

  # Store the target created by swig_add_module in a more friendly name:
  set(_swig_target ${SWIG_MODULE_${module_name}_REAL_NAME})
  qi_use_lib(${_swig_target} PYTHON ${ARG_DEPENDS})

  # Fix output directory
  set_target_properties(${_swig_target}
      PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY_DEBUG   "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        RUNTIME_OUTPUT_DIRECTORY_RELEASE "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        RUNTIME_OUTPUT_DIRECTORY         "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        ARCHIVE_OUTPUT_DIRECTORY_DEBUG   "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        ARCHIVE_OUTPUT_DIRECTORY_RELEASE "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        ARCHIVE_OUTPUT_DIRECTORY         "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        LIBRARY_OUTPUT_DIRECTORY_DEBUG   "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        LIBRARY_OUTPUT_DIRECTORY_RELEASE "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
        LIBRARY_OUTPUT_DIRECTORY         "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}"
  )

  if (WIN32)
  # Be sure a .pyd file gets created.
    set_target_properties(${_swig_target} PROPERTIES SUFFIX   ".pyd")
  endif()

  if(APPLE)
     get_target_property(_output_path ${_swig_target} LIBRARY_OUTPUT_DIRECTORY)
     file(RELATIVE_PATH _dotdot ${_output_path} "${QI_SDK_DIR}/${QI_SDK_LIB}")
     set_target_properties("${_swig_target}"
       PROPERTIES
         INSTALL_RPATH "@loader_path/${_dotdot};@loader_path/${_dotdot}..")
  endif()

  qi_install_python(TARGETS ${_swig_target} SUBFOLDER ${ARG_SUBFOLDER})

  qi_install_python("${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}/${module_name}.py" SUBFOLDER ${ARG_SUBFOLDER})

  ## FIXME: factorize this with qi_create_python_ext
  # Register the target into the build dir for qipy
  file(WRITE ${QI_SDK_DIR}/qi.pth
    "${QI_SDK_DIR}/${QI_SDK_LIB}/python2.7/site-packages${_subfolder}\n"
  )

  set(SWIG_MODULE_${module_name}_REAL_NAME ${_swig_target} PARENT_SCOPE)
endfunction()
