## Copyright (c) 2012 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Staging targets
# ================
#
# This module make libraries and executables build in this projects available
# to others projects.
#

include(qibuild/internal/stage)
include(qibuild/internal/uselib)

#! Generate a 'name'-config.cmake, allowing other project to find the library.
# \arg:target a target created with qi_create_lib
# \group:DEPRECATED specify a deprecated message. This message will be displayed
#                   each time another project use that lib.
# \group:DEPENDS if not given, ${TARGET}_DEPENDS will be guessed from
#                the previous calls to qi_use_lib().
#                Use this (whith care!) to override this behavior.
# \group:INCLUDE_DIRS it not given, ${TARGET}_INCLUDE_DIRS  will be
#                 guessed from the previous calls to
#                 include_directories()
#                 Use this (whith care!) to override this behavior.
# \group:DEFINITIONS list of compilation flags targets depending
#                 of this library should use.
# \group:PATH_SUFFIXES when your header is installed in foo/bar.h,
#                 but you still need to do #include <bar.h>, you can
#                 set PATH_SUFFIXES to 'foo'. Be careful to test the
#                 intall rules of your headers if you choose to do so.
function(qi_stage_lib target)
  if(NOT TARGET "${target}")
    qi_error("When calling qi_stage_lib(${target})
    No such target.

    Please make sure the target exists, and that qi_stage_lib
    is called *after* qi_create_lib and qi_use_lib
    ")
  endif()
  _qi_internal_stage_lib(${target} ${ARGN})
endfunction()

#! Generate a 'name'-config.cmake, allowing other project to find the library.
# This library does not have to be a cmake target, it's a header only library.
# \arg:target a target created with qi_create_lib
# \group:DEPRECATED specify a deprecated message. This message will be displayed
#                   each time another project use that lib.
# \group:DEPENDS if not given, ${TARGET}_DEPENDS will be guessed from
#                the previous calls to qi_use_lib().
#                Use this (whith care!) to override this behavior.
# \group:INCLUDE_DIRS it not given, ${TARGET}_INCLUDE_DIRS  will be
#                 guessed from the previous calls to
#                 include_directories()
#                 Use this (whith care!) to override this behavior.
# \group:DEFINITIONS list of compilation flags targets depending
#                 of this library should use.
# \group:PATH_SUFFIXES when your header is installed in foo/bar.h,
#                 but you still need to do #include <bar.h>, you can
#                 set PATH_SUFFIXES to 'foo'. Be careful to test the
#                 intall rules of your headers if you choose to do so.
function(qi_stage_header_only_lib target)
  _qi_internal_stage_header_only_lib(${target} ${ARGN})
endfunction()

#! not implemented yet
function(qi_stage_bin)
  qi_error("qi_stage_bin: not implemented")
endfunction()

#! not implemented yet
function(qi_stage_script)
  qi_error("qi_stage_script: not implemented")
endfunction()

#! stage a cmake file
# For instance, assuming you have a foo-config.cmake file
# containing my_awesome_function, you can do::
#
#   qi_stage_cmake("foo-config.cmake")
#
# Then later, (in an other project, or in the same project)::
#
#   find_package(foo)
#   my_awesome_function()
#
# \arg : module  path to the module file, relative to
#               CMAKE_CURRENT_SOURCE_DIR
#
function(qi_stage_cmake module_file)
  if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${module_file}")
    qi_error("

    Could not stage ${module_file}:
    ${CMAKE_CURRENT_SOURCE_DIR}/${module_file}
    does not exist
    ")

  endif()

  get_filename_component(_basename "${module_file}" NAME)

  # module_file is something like foo/bar/baz-config.cmake, or
  # foo/bar/bazConfig.cmake, and we need to install it to
  # share/cmake/baz/baz-config.cmake

  string(REGEX MATCH "-config\\.cmake$" _match "${_basename}")
  if(_match)
    string(REPLACE "-config.cmake" "" _module_name "${_basename}")
  else()
    string(REGEX MATCH "Config\\.cmake" _match "${_basename}")
    if(_match)
      string(REPLACE "Config.cmake" "" _module_name "${_basename}")
    else()
      qi_error("
        Could not stage ${module_file}:
        The file name should end with \"-config.cmake\"
        or \"Config.cmake\" (deprecated)
      ")
    endif()
  endif()

  file(COPY "${module_file}"
       DESTINATION
       "${QI_SDK_DIR}/${QI_SDK_CMAKE_MODULES}/")

  qi_install_cmake("${module_file}" SUBFOLDER "${_module_name}")

endfunction()


#! Handles dependencies between projects.
#
# Call find_package for you, then do all the include_directories
# and target_link_libraries that are needed.
#
# .. note:: The name must be an existing target, so you must call
#     ``qi_use_lib`` **after** :cmake:function:`qi_create_bin` or :cmake:function:`qi_create_lib`
#
# You can however call ``qi_use_lib`` several times, for instance::
#
#  qi_create_bin(foo)
#
#  ...
#
#  qi_use_lib(foo bar)
#  if(UNIX)
#     qi_use_lib(foo PTHREAD)
#  endif()
#
# \arg:name The target to add dependencies to.
# \argn: dependencies
#
#
function(qi_use_lib name)
  if(QI_${name}_TARGET_DISABLED)
    qi_warning("When calling qi_use_lib(${name})

    This target is disabled, ignoring this call
    ")
    return()
  endif()
  if(NOT TARGET "${name}")
    qi_error("When calling qi_use_lib(${name})
    No such target: ${name}
    Make sure you call qi_use_lib after qi_create_bin or
    qi_create_lib
    ")
    return()
  endif()
  _qi_use_lib_internal(${name} ${ARGN})
endfunction()
