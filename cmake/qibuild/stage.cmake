## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

#! Staging targets
# ================
#
# This module make libraries and executables build in this projects available
# to others projects.
#

include(qibuild/internal/stage)
include(qibuild/internal/list)
include(qibuild/internal/uselib)

#! Generate a 'name'-config.cmake, allowing other project to find the library.
# Usage of the various arguments are a bit tricky, so please read
# :ref:`using-qi-stage-lib` before using them
#
# \arg:target a target created with qi_create_lib
# \group:DEPRECATED specify a deprecated message. This message will be displayed
#                   each time another project use that lib.
# \group:DEPENDS if not given, ${TARGET}_DEPENDS will be guessed from
#                the previous calls to qi_use_lib().
#                Use this (with care!) to override this behavior.
#                One should list all the (public) "direct" dependencies *and*
#                their (public) dependencies.
# \group:INCLUDE_DIRS if not given, ${TARGET}_INCLUDE_DIRS  will be
#                 guessed from the previous calls to
#                 include_directories()
#                 Use this (with care!) to override this behavior.
# \group:PATH_SUFFIXES when your header is installed in foo/bar.h,
#                 but you still need to do #include <bar.h>, you can
#                 set PATH_SUFFIXES to 'foo'. Be careful to test the
#                 install rules of your headers if you choose to do so.
#
function(qi_stage_lib target)
  if(NOT TARGET "${target}")
    qi_error("When calling qi_stage_lib(${target})
    No such target.

    Please make sure the target exists, and that qi_stage_lib
    is called *after* qi_create_lib and qi_use_lib
    ")
  endif()
  get_target_property(_target_type ${target} TYPE)
  if("${_target_type}" STREQUAL "EXECUTABLE")
    qi_error("When calling qi_stage_lib(${target})
    Target is an executable, expecting a library
    ")
  endif()
  _qi_internal_stage_lib(${target} ${ARGN})
endfunction()

#! Generate a 'name'-config.cmake, allowing other projects to find the
# header-only library.
# If the library has some dependencies, use something like::
#
#       find_package(FOO)
#       include_directories(${FOO_INCLUDE_DIRS})
#       qi_stage_header_only_lib(bar DEPENDS FOO)
#
# \arg:name the name of the library, clients of the library can use
#           ``qi_use_lib(... NAME)``
# \group:DEPRECATED specify a deprecated message. This message will be displayed
#                   each time another project use that lib.
# \group:DEPENDS if not given, ${NAME}_DEPENDS will be empty
#                the previous calls to qi_use_lib().
# \group:INCLUDE_DIRS if not given, ${NAME}_INCLUDE_DIRS  will be
#                 guessed from the previous calls to
#                 include_directories()
#                 Use this (with care!) to override this behavior.
# \group:PATH_SUFFIXES when your header is installed in foo/bar.h,
#                 but you still need to do #include <bar.h>, you can
#                 set PATH_SUFFIXES to 'foo'. Be careful to test the
#                 install rules of your headers if you choose to do so.
function(qi_stage_header_only_lib target)
  _qi_internal_stage_header_only_lib(${target} ${ARGN})
endfunction()

#! Generate a 'name'-config.cmake, allowing other projects
# to find the binary
#
# Example ::
#
#   # in foo/CMakeLists.txt
#   qi_create_bin(foo foo.cpp)
#   qi_stage_bin(foo)
#
#   # in bar/CMakeLists.txt:
#   find_package(foo)
#   # Do something with ${FOO_EXECUTABLE}
# \arg: target  the name of a target
function(qi_stage_bin target)
  if(NOT TARGET "${target}")
    qi_error("When calling qi_stage_bin(${target})
    No such target.

    Please make sure the target exists, and that qi_stage_bin
    is called *after* qi_create_bin
    ")
  endif()
  get_target_property(_target_type ${target} TYPE)
  if(NOT "${_target_type}" STREQUAL "EXECUTABLE")
    qi_error("When calling qi_stage_bin(${target})
    Target is not an executable.
    ")
  endif()
  _qi_internal_stage_bin(${target} ${ARGN})
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


#! Stage an executable script
#
# Will stage a cmake file so
# that others can locate the script. Use like this::
#
#     qi_stage_script(src/myscript)
#
# And in other projects::
#
#     find_package(myscript)
#     use_script_in_function(${MYSCRIPT_EXECUTABLE})
#
# \arg:file_name Path to the script in source dir.
# \flag:TRAMPOLINE If set, will generate a trampoline script in
# sdk binary dir. Use this flag if your script uses any element
# that is built.
# \flag:PYTHON set if script is written in python
# \group:DEPENDS list of target or packages this script depends on.
#                Used for trampoline script generation only.
function(qi_stage_script file_name)
  cmake_parse_arguments(ARG
  "TRAMPOLINE;PYTHON"
  ""
  "DEPENDS"
  ${ARGN})
  if(NOT EXISTS "${CMAKE_CURRENT_SOURCE_DIR}/${module_file}")
    qi_error("

    Could not stage ${module_file}:
    ${CMAKE_CURRENT_SOURCE_DIR}/${module_file}
    does not exist
    ")
  endif()
  if(ARG_TRAMPOLINE)
     if(ARG_PYTHON)
        set(_PYTHON PYTHON)
     endif()
     get_filename_component(target "${file_name}" NAME)
     _qi_internal_stage_script("${file_name}" "${QI_SDK_DIR}/${QI_SDK_BIN}/${target}")
     qi_generate_trampoline("${target}" "${file_name}" DEPENDS ${ARG_DEPENDS} ${_PYTHON})
  else()
    _qi_internal_stage_script("${file_name}" "${CMAKE_CURRENT_SOURCE_DIR}/${file_name}")
  endif()
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
#  # ...
#
#  qi_use_lib(foo bar)
#  if(UNIX)
#     qi_use_lib(foo PTHREAD)
#  endif()
#
# \arg:name The target to add dependencies to.
# \argn: dependencies
# \flag:ASSUME_SYSTEM_INCLUDE  Use ``-isystem`` for
#       including dependencies.
#       Useful for instance to ignore warnings coming
#       from 3rd party headers.
#
function(qi_use_lib name)
  if(NOT TARGET "${name}")
    qi_error("When calling qi_use_lib(${name})
    No such target: ${name}
    ")
    return()
  endif()
  _qi_use_lib_internal(${name} ${ARGN})
endfunction()

#!
#  Make sure configuration and data files in the
#  given directory can be found by
#  ``qi::findData()`` in this project or
#  any dependency
#
# For this to work, configuration files should be
# in ``etc`` and data files in ``share``
#
# Note that this function does not create any install rule,
# so you should call qi_install_data(share/... ) for
# the files to be found after your project is installed.
#
# See :ref:`cmake-data`
#
# \arg:directory (optional): the directory to
#                 register, relative to
#                 CMAKE_CURRENT_SOURCE_DIR. Defaults
#                 to CMAKE_CURRENT_SOURCE_DIR
#
function(qi_stage_dir)
  set(_path_conf "${QI_SDK_DIR}/${QI_SDK_SHARE}/qi/path.conf")
  set(_dirs)
  if(EXISTS "${_path_conf}")
    file(STRINGS "${_path_conf}" _dirs)
  endif()
  # fixme: error when more than one arg
  if(${ARGV1})
    qi_error("qi_stage_dir must be called with zero or one argument")
  endif()
  if(ARGV0)
    get_filename_component(_to_stage ${ARGV0} ABSOLUTE)
  else()
    set(_to_stage "${CMAKE_CURRENT_SOURCE_DIR}")
  endif()
  _qi_list_prepend_uniq(_dirs ${_to_stage})
  # re-create the file:
  file(WRITE "${_path_conf}" "")
  foreach(_dir ${_dirs})
    file(APPEND "${_path_conf}" "${_dir}\n")
  endforeach()
endfunction()


#!
# Register the given path as a CMAKE_PREFIX_PATH.
#
# Used when pre-compiled binaries are put under version control.
#
# Note that the pre-compiled SDK must have the following layout:
#
# .. code-block:: console
#
#   lib
#     libfoo.so
#   include
#     foo
#       foo.h
#   share
#     cmake
#       foo
#         foo-config.cmake
#
# \arg:path: the path to the pre-compiled SDK
function(qi_add_bin_sdk path)
  # Generate a -config.cmake in the build dir that includes the one
  # put in share/cmake/

  file(GLOB _cmake_files "${path}/share/cmake/*/*.cmake")
  foreach(_cmake_file ${_cmake_files})
    get_filename_component(_name ${_cmake_file} NAME)
    set(_to_write "${QI_SDK_DIR}/${QI_SDK_CMAKE_MODULES}/${_name}")
    file(WRITE ${_to_write} "
include(\"${_cmake_file}\")
")
  endforeach()

  # Generate install rules
  install(DIRECTORY "${path}/lib" DESTINATION "/"
    USE_SOURCE_PERMISSIONS
    COMPONENT runtime
    PATTERN "*.a" EXCLUDE
  )
  install(DIRECTORY "${path}/lib" DESTINATION "/"
    COMPONENT devel
    PATTERN "*.a"
  )
  install(DIRECTORY "${path}/include" DESTINATION "/"
    COMPONENT devel
  )
  install(DIRECTORY "${path}/share/cmake" DESTINATION "share"
    COMPONENT devel
  )

endfunction()
