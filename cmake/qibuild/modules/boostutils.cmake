## Copyright (c) 2012-2019 SoftBank Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

function(boost_flib _prefix)
  if(${ARGC} GREATER 1)
    set(_libnames ${ARGN})
  else()
    set(_libnames ${_prefix})
  endif()

  string(TOUPPER ${_prefix} _prefix)
  set(_prefix "BOOST_${_prefix}")

  clean(${_prefix})
  # Required so that FindBoost.cmake does not try to include this file
  set(Boost_NO_BOOST_CMAKE TRUE)
  # Use shared libraries everywhere
  set(Boost_USE_STATIC_LIBS OFF)
  if(MSVC)
    qi_persistent_append(${_prefix}_DEFINITIONS  "BOOST_ALL_DYN_LINK")
    qi_persistent_append(${_prefix}_DEFINITIONS  "BOOST_ALL_NO_LIB")
    # fix compilation without bcrypt
    qi_persistent_append(${_prefix}_DEFINITIONS  "BOOST_UUID_FORCE_AUTO_LINK")
  endif()

  foreach(_libname ${_libnames})
    clean(Boost)
    find_package(Boost COMPONENTS "${_libname}" QUIET)
    if(Boost_FOUND)
      break()
    endif()
  endforeach()

  # fix compilation in cmake v2.8.11.2
  # some of the qibuild cmake configs refer to this variable
  set(Boost_VERSION "${Boost_VERSION}" PARENT_SCOPE)

  qi_persistent_set(${_prefix}_INCLUDE_DIRS ${Boost_INCLUDE_DIRS})
  if(DEFINED Boost_LIBRARIES)
    qi_persistent_set(${_prefix}_LIBRARIES    ${Boost_LIBRARIES})
    export_lib(${_prefix})
  else()
    export_header(${_prefix})
  endif()
endfunction()
