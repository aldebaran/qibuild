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
# create a new executable binary
#
###########################
function(create_bin _name)
  subfolder_parse_args(_subfolder _args ${ARGN})
  parse_is_options(_args1 NO_INSTALL _no_install ${_args})
  parse_is_options(_args2 EXCLUDE_FROM_ALL _exclude_from_all ${_args1})

  if (_exclude_from_all)
    set(_no_install ON)
  endif()

  debug("BINLIB: create_bin: (${_name}, ${_subfolder}, ${_args1})")

  if (${_exclude_from_all})
    add_executable("${_name}" EXCLUDE_FROM_ALL ${_args2})
  else()
    add_executable("${_name}"  ${_args2})
  endif()
  #always postfix debug lib/bin with _d
  if(${TARGET_ARCH} STREQUAL windows)
    set_target_properties("${_name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif()
  set(${_name}_SUBFOLDER ${_subfolder} CACHE INTERNAL "" FORCE)

  #make install rules
  if(_no_install)
    debug("libbin: create_bin: ${_name} not to be installed")
    set(${_name}_NO_INSTALL TRUE CACHE INTERNAL "" FORCE)
  else()
    install(TARGETS "${_name}"
            RUNTIME COMPONENT binary DESTINATION ${_SDK_BIN}/${_subfolder})
  endif()

  if(${TARGET_ARCH} STREQUAL windows)
    win32_copy_target("${_name}" "${SDK_DIR}/${_SDK_BIN}/${_subfolder}")
    # Be nice with VS user: generate a vcproj so that:
    # -> target path is the path where the executable is copyied
    # (not the place where it is compiled)
    # -> PATH and PYTHONPATH are always set to nice values
    configure_user_vcproj(${_name} "${SDK_DIR}/${_SDK_BIN}/${_subfolder}")
  else()
    set_target_properties(  "${_name}" PROPERTIES RUNTIME_OUTPUT_DIRECTORY ${SDK_DIR}/${_SDK_BIN}/${_subfolder})
  endif()
endfunction(create_bin)


###########################
#
# create a new script
#
###########################
function(create_script _name _namein)
  subfolder_parse_args(_subfolder _args ${ARGN})
  parse_is_options(_args1 NO_INSTALL _no_install ${_args})
  debug("BINLIB: create_script: (${_name}, ${_namein}, ${_subfolder})")
  copy_with_depend("${_namein}" "${_SDK_BIN}/${_subfolder}/${_name}")
  set(${_name}_SUBFOLDER ${_subfolder} CACHE INTERNAL "" FORCE)


  #make install rules
  if (${_no_install})
    debug("libbin: create_script: ${_name} not to be installed")
    set(${_name}_NO_INSTALL TRUE CACHE INTERNAL "" FORCE)
  else()
    install(PROGRAMS
            "${SDK_DIR}/${_SDK_BIN}/${_subfolder}/${_name}"
            COMPONENT binary
            DESTINATION
            "${_SDK_BIN}")
  endif()
endfunction(create_script)

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
# add a new library
# @param _cmakename : the name used in use_lib to build with this lib typically "LIBFOO"
# @param _name      : the target name for example "foo"
#
# A SUBFOLDER <subfolder> keyword is available to specify a subfolder for install/compil
#
###########################
function(create_lib _name)
  parse_is_options(_args0 NO_INSTALL _no_install  ${ARGN})
  parse_is_options(_args1 "NOBINDLL" _is_nobinwin ${_args0})
  set(${_name}_NO_INSTALL CACHE INTERNAL "" FORCE)
  subfolder_parse_args(_subfolder _args2 ${_args1})
  subargs_parse_args("SRC"      "HEADER;RESOURCE;" _src    _args3 ${_args2})
  subargs_parse_args("HEADER"   "SRC;RESOURCE;"    _header _args4 ${_args3})
  subargs_parse_args("RESOURCE" "SRC;HEADER;"      _res    _args  ${_args4})
  debug("BINLIB: create_lib: (${_name}, ${_is_nobinwin}, ${_subfolder}, src=(${_args} ${_src}) , h=(${_header}))")

  add_library("${_name}" ${_args} ${_src} ${_header})
  #always postfix debug lib/bin with _d
  if (${TARGET_ARCH} STREQUAL windows)
    set_target_properties("${_name}" PROPERTIES DEBUG_POSTFIX "_d")
  endif (${TARGET_ARCH} STREQUAL windows)

  #by default dll under windows goes in bin
  #everything else goes into lib
  if (_is_nobinwin)
    set(_binlib "${_SDK_LIB}")
  else (_is_nobinwin)
    get_target_property(_ttype ${_name} "TYPE")
    if (_ttype STREQUAL "STATIC_LIBRARY")
      set(_binlib "${_SDK_LIB}")
    else (_ttype STREQUAL "STATIC_LIBRARY")
      set(_binlib "${_SDK_BIN}")
    endif (_ttype STREQUAL "STATIC_LIBRARY")
  endif (_is_nobinwin)

  set(${_name}_SUBFOLDER ${_subfolder} CACHE INTERNAL "" FORCE)
  if (_res)
    set_target_properties("${_name}" PROPERTIES RESOURCE      "${_res}")
  endif (_res)
  if (_header)
    set_target_properties("${_name}" PROPERTIES PUBLIC_HEADER "${_header}")
  endif (_header)

  #under win32 bin/lib goes into /Release and /Debug => change that
  if (${TARGET_ARCH} STREQUAL windows)
    win32_copy_target("${_name}" "${SDK_DIR}/${_binlib}/${_subfolder}")
  else (${TARGET_ARCH} STREQUAL windows)
    set_target_properties("${_name}"
      PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY ${SDK_DIR}/${_binlib}/${_subfolder}
        ARCHIVE_OUTPUT_DIRECTORY ${SDK_DIR}/${_SDK_LIB}/${_subfolder}
        LIBRARY_OUTPUT_DIRECTORY ${SDK_DIR}/${_SDK_LIB}/${_subfolder}
      )
  endif (${TARGET_ARCH} STREQUAL windows)

  #make install rules
  if (${_no_install})
    debug("libbin: create_script: ${_name} not to be installed")
    set(${_name}_NO_INSTALL TRUE CACHE INTERNAL "" FORCE)
  else()
    install(TARGETS "${_name}"
            RUNTIME COMPONENT binary     DESTINATION ${_binlib}/${_subfolder}
            LIBRARY COMPONENT lib        DESTINATION ${_SDK_LIB}/${_subfolder}
      PUBLIC_HEADER COMPONENT header     DESTINATION ${_SDK_INCLUDE}/${_subfolder}
     PRIVATE_HEADER COMPONENT header     DESTINATION ${_SDK_INCLUDE}/${_subfolder}
           RESOURCE COMPONENT data       DESTINATION ${_SDK_SHARE}/${_name}/${_subfolder}
            ARCHIVE COMPONENT static-lib DESTINATION ${_SDK_LIB}/${_subfolder})
  endif()
  debug("BINLIB: END create_lib: (${_name}, ${_is_nobinwin}, ${_subfolder}, src=(${_args} ${_src}) , h=(${_header}))")
endfunction(create_lib)


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
