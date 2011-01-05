##
## compat-bad.cmake
## Login : <ctaf42@cgestes-de2>
## Started on  Wed Jan  5 12:16:56 2011 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2011 Cedric GESTES
## This program is free software; you can redistribute it and/or modify
## it under the terms of the GNU General Public License as published by
## the Free Software Foundation; either version 3 of the License, or
## (at your option) any later version.
##
## This program is distributed in the hope that it will be useful,
## but WITHOUT ANY WARRANTY; without even the implied warranty of
## MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
## GNU General Public License for more details.
##
## You should have received a copy of the GNU General Public License
## along with this program; if not, write to the Free Software
## Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307 USA
##

function(_try_install_dir _dir)
  if (EXISTS ${_dir})
    install(DIRECTORY ${_dir} ${ARGN})
  elseif (EXISTS ${CMAKE_CURRENT_SOURCE_DIR}/${_dir})
    install(DIRECTORY ${_dir} ${ARGN})
  endif()
endfunction()

function(_win_install_dlls _src _dest)
  file(GLOB _dlls "${_src}/*.dll")
  install(FILES
    ${_dlls}
    COMPONENT lib
    DESTINATION ${_dest}
  )
endfunction()

function(install_multiarch_binary)
  set(_runtime_lib ".*\\.(dll|dylib|so.?.*)$")
  set(_devel_lib ".*(a|lib)$")
  set(_python_lib ".*(py|pyd)$")

  _try_install_dir("common/include/"    USE_SOURCE_PERMISSIONS COMPONENT header     DESTINATION "${_SDK_INCLUDE}")
  _try_install_dir("common/lib/"        USE_SOURCE_PERMISSIONS COMPONENT lib        DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_runtime_lib}")
  _try_install_dir("common/lib/"        USE_SOURCE_PERMISSIONS COMPONENT python     DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_python_lib}")
  _try_install_dir("common/lib/"        USE_SOURCE_PERMISSIONS COMPONENT static-lib DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_devel_lib}")
  _try_install_dir("common/bin/"        USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_BIN}")
  _try_install_dir("common/Frameworks/" USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_FRAMEWORK}")

  _try_install_dir("${TARGET_ARCH}/include/"     USE_SOURCE_PERMISSIONS COMPONENT header     DESTINATION "${_SDK_INCLUDE}")

  if(WIN32)
    _win_install_dlls("${TARGET_ARCH}/lib" "${_SDK_BIN}")
  else()
    _try_install_dir("${TARGET_ARCH}/lib/"       USE_SOURCE_PERMISSIONS COMPONENT lib        DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_runtime_lib}")
  endif()

  _try_install_dir("${TARGET_ARCH}/lib/"         USE_SOURCE_PERMISSIONS COMPONENT python     DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_python_lib}")
  _try_install_dir("${TARGET_ARCH}/lib/"         USE_SOURCE_PERMISSIONS COMPONENT static-lib DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_devel_lib}")
  _try_install_dir("${TARGET_ARCH}/bin/"         USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_BIN}")
  _try_install_dir("${TARGET_ARCH}/Frameworks/"  USE_SOURCE_PERMISSIONS COMPONENT binary     DESTINATION "${_SDK_FRAMEWORK}")

  if (TARGET_SUBARCH)
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/include/"    USE_SOURCE_PERMISSIONS   COMPONENT header     DESTINATION "${_SDK_INCLUDE}")

    if(WIN32)
    _win_install_dlls("${TARGET_ARCH}-${TARGET_SUBARCH}/lib" "${_SDK_BIN}")
    else()
      _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/lib/"      USE_SOURCE_PERMISSIONS   COMPONENT lib        DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_runtime_lib}")
    endif()

    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/lib/"        USE_SOURCE_PERMISSIONS   COMPONENT python     DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_python_lib}")
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/lib/"        USE_SOURCE_PERMISSIONS   COMPONENT static-lib DESTINATION "${_SDK_LIB}" FILES_MATCHING REGEX "${_devel_lib}")
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/bin/"        USE_SOURCE_PERMISSIONS   COMPONENT binary     DESTINATION "${_SDK_BIN}")
    _try_install_dir("${TARGET_ARCH}-${TARGET_SUBARCH}/Frameworks/" USE_SOURCE_PERMISSIONS   COMPONENT binary     DESTINATION "${_SDK_FRAMEWORK}")
  endif(TARGET_SUBARCH)
endfunction()

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

function(generate_revision_header _name _revision)
  string(TOUPPER ${_name} NAME)

  set(TO_WRITE_IN
"
#ifndef @NAME@_REVISION_H
#define @NAME@_REVISION_H

#define @NAME@_REVISION \"@_revision@\"


#endif // ! @NAME@_REVISION_H
"
)

# First, we write a temporary header in CMAKE_CURRENT_BINARY_DIR my_module_revision.temp.h
# We only overwrite CMAKE_CURRENT_BINARY_DIR/my_module_revision.h is my_module_revision.temp.h
# has changed.

# This is to avoid too many recompilations
  string(CONFIGURE ${TO_WRITE_IN} TO_WRITE_OUT @ONLY)
  configure_file("${T001CHAIN_DIR}/cmake/templates/revision.in"
                 "${CMAKE_CURRENT_BINARY_DIR}/include/${_name}_revision.h" @ONLY)
  include_directories("${CMAKE_CURRENT_BINARY_DIR}/include")
endfunction()

function(set_cpack_version_from_git MODULENAME)
  string(REGEX MATCH "v?([0-9]*\\.[0-9]*)\\.([0-9]*(-rc[0-9]+)?)[\\.\\-]?(.*)" _out ${${MODULENAME}_REVISION})
  # CMAKE_MATCH_0 contains the whole match
  # CMAKE_MATCH_3 optionaly contains the [rct] part
  if (CMAKE_MATCH_4 STREQUAL "")
    set(CMAKE_MATCH_4 "0")
  endif()
  set(CPACK_PACKAGE_VERSION_MAJOR ${CMAKE_MATCH_1} PARENT_SCOPE)
  set(CPACK_PACKAGE_VERSION_MINOR ${CMAKE_MATCH_2} PARENT_SCOPE)
  set(CPACK_PACKAGE_VERSION_PATCH ${CMAKE_MATCH_4} PARENT_SCOPE)
endfunction()
