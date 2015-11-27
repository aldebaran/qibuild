## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

cmake_minimum_required(VERSION 2.8.12.2)

#yeah allow NORMAL endfunction/endif/..
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)
# Bad variable reference syntax is an error.
cmake_policy(SET CMP0010 NEW)
#cmake policy push/pop policies before including another cmake
cmake_policy(SET CMP0011 NEW)
# if() recognizes numbers and boolean constants.
cmake_policy(SET CMP0012 NEW)
# Prefer files from the CMake module directory when including from there.
cmake_policy(SET CMP0017 NEW)

include("qibuild/version")
message(STATUS "Using qibuild ${QIBUILD_VERSION}")
include("qibuild/log")
include("qibuild/set")


include("qibuild/subdirectory")
include("qibuild/internal/layout")
include("qibuild/internal/install")
include("qibuild/internal/glob")

if (NOT QI_SDK_DIR)
  qi_persistent_set(QI_SDK_DIR "${CMAKE_BINARY_DIR}/sdk")
endif()

#ensure CMAKE_BUILD_TYPE is either Debug or Release
if (CMAKE_BUILD_TYPE STREQUAL "")
  qi_persistent_set(CMAKE_BUILD_TYPE "Debug")
endif()

if("${CMAKE_BUILD_TYPE}" STREQUAL "Debug")
  set(_default_debug_info ON)
else()
  set(_default_debug_info OFF)
endif()

option(QI_WITH_COVERAGE "Enable code coverage" OFF)
option(QI_WITH_DEBUG_INFO "Default is to follow CMAKE_BUILD_TYPE"
      ${_default_debug_info})
option(QI_FORCE_32_BITS "Force 32bits build even when on 64bits" OFF)

include("qibuild/python")
include("qibuild/find")
include("qibuild/flags")
include("qibuild/tests")
include("qibuild/install")
include("qibuild/target")
include("qibuild/submodule")
include("qibuild/stage")
include("qibuild/option")
include("qibuild/codegen")
include("qibuild/gettext")
include("qibuild/git")

# Find libraries from self sdk dir before everything else.
qi_persistent_prepend_uniq(CMAKE_PREFIX_PATH "${QI_SDK_DIR}")


if (QI_T001CHAIN_COMPAT)
  include("qibuild/compat/compat")
endif()

# temporary work around for ubuntu >= natty and cmake < 2.8.6
# (inspired by http://www.cmake.org/Bug/view.php?id=12037

find_program(_dpkg_architecture dpkg-architecture)
# make it internal so the user does not see it:
set(_dpkg_architecture ${_dpkg_architecture} CACHE INTERNAL "" FORCE)

if(_dpkg_architecture)
  execute_process(
    COMMAND dpkg-architecture -qDEB_HOST_MULTIARCH
    OUTPUT_VARIABLE _arch_triplet
    ERROR_QUIET
    OUTPUT_STRIP_TRAILING_WHITESPACE
    RESULT_VARIABLE _ret)
  if(${_ret} EQUAL 0)
    list(APPEND CMAKE_SYSTEM_LIBRARY_PATH /usr/lib/${_arch_triplet})
  endif()
endif()

if (DEFINED  CMAKE_PREFIX_PATH)
  list(REVERSE           CMAKE_PREFIX_PATH)
  list(REMOVE_DUPLICATES CMAKE_PREFIX_PATH)
  list(REVERSE           CMAKE_PREFIX_PATH)
endif()
if (DEFINED  CMAKE_PREFIX_PATH)
  list(REVERSE           CMAKE_PREFIX_PATH)
  list(REMOVE_DUPLICATES CMAKE_PREFIX_PATH)
  list(REVERSE           CMAKE_PREFIX_PATH)
endif()
if (DEFINED  CMAKE_MODULE_PATH)
  list(REVERSE           CMAKE_MODULE_PATH)
  list(REMOVE_DUPLICATES CMAKE_MODULE_PATH)
  list(REVERSE           CMAKE_MODULE_PATH)
endif()

qi_debug("CMAKE_PREFIX_PATH  = ${CMAKE_PREFIX_PATH}")
qi_debug("CMAKE_PREFIX_PATH     = ${CMAKE_PREFIX_PATH}")
qi_debug("CMAKE_MODULE_PATH     = ${CMAKE_MODULE_PATH}")
qi_debug("CMAKE_INCLUDE_PATH    = ${CMAKE_INCLUDE_PATH}")
qi_debug("CMAKE_SYSTEM_LIBRARY_PATH = ${CMAKE_SYSTEM_LIBRARY_PATH}")


# Small option to deactivate targets created by qi_add_test et al.
option(QI_WITH_TESTS
  "If OFF, no test will be built, and `qibuild test` won't run any test"
  ON)
option(QI_WITH_PERF_TESTS "Triggers building of perf tests" OFF)
option(QI_WITH_NIGHTLY_TESTS "triggers building of nightly tests" OFF)

# For compatibility with qibuild 3.1
qi_persistent_set(BUILD_TESTS ${QI_WITH_TESTS})
qi_persistent_set(BUILD_PERF_TESTS ${QI_WITH_PERF_TESTS})
qi_persistent_set(QI_NIGHTLY_TESTS ${QI_WITH_NIGHTLY_TESTS})

# change default for CMAKE_INSTALL_PREFIX
# (it's c:\program files\<project> on Windows, and
# /usr/local elsewhere)
if(CMAKE_INSTALL_PREFIX_INITIALIZED_TO_DEFAULT)
  qi_persistent_set(CMAKE_INSTALL_PREFIX "/")
endif()

# Install a share/qi/path.conf so that libqi's sdkPrefix can be found
file(WRITE "${CMAKE_BINARY_DIR}/path.conf" "# Installed by qibuild. Do not remove\n")
qi_install_data(${CMAKE_BINARY_DIR}/path.conf SUBFOLDER "qi")

# Avoid warning about unused variable:
qi_persistent_set(QI_VIRTUALENV_PATH ${QI_VIRTUALENV_PATH})
