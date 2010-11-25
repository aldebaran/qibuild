##
## binlib.cmake
## Login : <ctaf@localhost.localdomain>
## Started on  Mon Sep 29 14:35:02 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008, 2010 Aldebaran Robotics


if (NOT _BINLIB_CMAKE_)
set(_BINLIB_CMAKE_ TRUE)


#####
# Create a suitable vc_proj from a target created by create_bin
# _name     : name of cmake target (first arg of create_bin)
# _location : where the target has been built (build/sdk/bin/name.exe)
#####
function(configure_user_vcproj _name _location)
  file(TO_NATIVE_PATH ${_location} _native_location)
  file(TO_NATIVE_PATH ${SDK_DIR} NATIVE_SDK_DIR)
  set(USER $ENV{USERNAME})
  site_name(REMOTE_MACHINE)
  # REMOTE_MACHINE now contains host name
  set(DEBUG_COMMAND   ${_native_location}\\${_name}_d.exe)
  set(RELEASE_COMMAND ${_native_location}\\${_name}.exe)
  set(_path $ENV{PATH})
  _gen_path(_sdk_path)
  set(_path "${_path};${_sdk_path}")
  set(ENV "PATH=${_path}")
  _gen_python_path(_python_path)
  set(ENV "${ENV}&#x0A;PYTHONPATH=${_python_path}")
  configure_file(
    ${T001CHAIN_DIR}/cmake/templates/vcproj.user.in
    ${CMAKE_CURRENT_BINARY_DIR}/${_name}.vcproj.${REMOTE_MACHINE}.${USER}.user
    @ONLY
  )
endfunction()




###########################
#
# copy a win32 target to a destination folder (merging debug/release)
#
###########################
function(win32_copy_target _name _dest)

  if (NOT WIN32)
    message(FATAL_ERROR "BINLIB: Win32_copy_target is not cross-plateform.")
    return()
  endif (NOT WIN32)

  check_is_target(${_name})

  # Quick and dirty, does not work if someone changed OUTPUT_NAME, DEBUG_PREFIX
  # or stuff like that ...
  set(${_name}_STAGED_PATH_RELEASE ${_dest}/${_name}.exe   CACHE INTERNAL "" FORCE)
  set(${_name}_STAGED_PATH_DEBUG   ${_dest}/${_name}_d.exe CACHE INTERNAL "" FORCE)

  file(TO_NATIVE_PATH "${_dest}/" _native_path)
  add_custom_command(TARGET ${_name} POST_BUILD
    COMMENT
      "copying target [${_name}] to ${_native_path}"
    COMMAND
      xcopy /C /Y \"\$\(TargetPath\)\" ${_native_path}
      )
endfunction(win32_copy_target)


###########################
#
# Create a pair of targets
# (both dynamic and static)
# Usage:
#
#   static_and_shared_libs(foo ${foo_srcs})
#
################################

# Generate a build/empty.cpp with nothing in it.
# Useful for create_static_and_shared_libs
function(_create_empty_source)
  if ((EXISTS ${CMAKE_BINARY_DIR}/empty.cpp))
    return()
  else()
    file(WRITE "${CMAKE_BINARY_DIR}/empty.cpp" "// This is an empty file")
  endif()
endfunction()

function(_get_a_single_source _OUT_result)
  # look for a .cpp file in ${sources}:
  set(_one_source)
  foreach( _source ${ARGN})
    if   (${_source} MATCHES ".*\\.cpp")
      set( _one_source ${_source})
      break()
    endif(${_source} MATCHES ".*\\.cpp")
  endforeach(_source ${_sources})
  if(NOT _one_source)
    foreach( _source ${ARGN})
      if   (${_source} MATCHES ".*\\.c")
        set( _one_source ${_source})
        break()
      endif(${_source} MATCHES ".*\\.c")
    endforeach(_source ${_sources})
  endif()
  set(${_OUT_result} ${_one_source} PARENT_SCOPE)
endfunction()

# this function does nothing on windows, because
# everything is already static anyway.

# on linux, this creates a shared and a static library,
# see http://www.cmake.org/Wiki/CMake_FAQ#Can_I_build_both_shared_and_static_libraries_with_one_ADD_LIBRARY_command.3F
# to see how we achieve this.
function(create_static_and_shared_libs _target_name)
  if(${TARGET_ARCH} STREQUAL windows)
    _create_static_and_shared_libs_win (${_target_name} ${ARGN})
    return()
  endif(${TARGET_ARCH} STREQUAL windows)
  if(APPLE)
    _create_static_and_shared_libs_mac (${_target_name} ${ARGN})
    return()
  endif()
  if(${SDK_ARCH} STREQUAL "linux")
    _create_static_and_shared_libs_linux(${_target_name} ${ARGN})
    return()
  endif()
# now on geode:
  create_lib(${_target_name} ${ARGN})
  return()
endfunction(create_static_and_shared_libs)

function(_create_static_and_shared_libs_linux _target_name)
  parse_is_options(_args "SHARED" _is_shared ${ARGN})
  create_lib(${_target_name}-static  STATIC ${_args})
  set_target_properties( ${_target_name}-static
    PROPERTIES
      COMPILE_FLAGS
        -fPIC)

  get_target_property(${_target_name}_STATIC_LOCATION ${_target_name}-static LOCATION)

  _create_empty_source()

  create_lib(${_target_name} SHARED "${CMAKE_BINARY_DIR}/empty.cpp")
    set_target_properties(${_target_name}
      PROPERTIES
        LINK_FLAGS
          " -Wl,-whole-archive \"${${_target_name}_STATIC_LOCATION}\" -Wl,-no-whole-archive ")

  target_link_libraries(${_target_name} ${_target_name}-static)

  # This is to be sure static lib is built first
  add_dependencies(${_target_name} ${_target_name}-static)
  set(${_target_name}_STATIC_AND_SHARED TRUE CACHE INTERNAL "" FORCE)
endfunction(_create_static_and_shared_libs_linux)

function(_create_static_and_shared_libs_win _target_name)
  create_lib(${_target_name} ${ARGN})
  return()
endfunction(_create_static_and_shared_libs_win)

function(_create_static_and_shared_libs_mac _target_name)
  create_lib(${_target_name} STATIC ${ARGN})
  return()
endfunction(_create_static_and_shared_libs_mac)


endif (NOT _BINLIB_CMAKE_)
