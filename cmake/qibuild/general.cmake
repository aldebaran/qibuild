## Copyright (C) 2011 Aldebaran Robotics

#yeah allow NORMAL endfunction/endif/..
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)
# Bad variable reference syntax is an error.
cmake_policy(SET CMP0010 NEW)
#cmake policy push/pop policies before including another cmake
cmake_policy(SET CMP0011 NEW)
# if() recognizes numbers and boolean constants.
cmake_policy(SET CMP0012 NEW)

# We use RUNTIME_DIRECTORY_<CONFIG> for visual studio
# which is a very nice feature but that only came up with
# cmake 2.8.2
if(MSVC_IDE)
  cmake_minimum_required(VERSION 2.8.3)
endif()

#get the current directory of the file
get_filename_component(_ROOT_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)

include("qibuild/log")
include("qibuild/set")

qi_append_global(CMAKE_PREFIX_PATH "${_ROOT_DIR}/modules/")

#include new cmake modules, when using old cmake
if(${CMAKE_VERSION} VERSION_LESS 2.8.3)
  qi_append_global(CMAKE_MODULE_PATH "${_ROOT_DIR}/upstream-backports")
endif()

set(QI_ROOT_DIR ${_ROOT_DIR})
set(QI_TEMPLATE_DIR ${_ROOT_DIR}/templates)

include("qibuild/subdirectory")
include("qibuild/internal/layout")
include("qibuild/internal/check")
include("qibuild/internal/install")
include("qibuild/internal/glob")
include("qibuild/internal/autostrap")

if (NOT QI_SDK_DIR)
  qi_set_global(QI_SDK_DIR "${CMAKE_BINARY_DIR}/sdk")
  qi_info("QI_SDK_DIR: ${QI_SDK_DIR}")
endif()

# always add SDK to FIND_ROOT_PATH when cross-compiling
if (DEFINED CMAKE_FIND_ROOT_PATH)
  qi_prepend_global(CMAKE_FIND_ROOT_PATH "${QI_SDK_DIR}")
  qi_debug("CMAKE_FIND_ROOT_PATH: ${CMAKE_FIND_ROOT_PATH}")
endif()

#force buildtype to be Upper case
if (DEFINED CMAKE_BUILD_TYPE)
  string(TOUPPER "${CMAKE_BUILD_TYPE}" "_BUILD_TYPE")
  qi_set_global(CMAKE_BUILD_TYPE "${_BUILD_TYPE}")
endif()

#ensure CMAKE_BUILD_TYPE is either Debug or Release
if (CMAKE_BUILD_TYPE STREQUAL "")
  qi_set_global(CMAKE_BUILD_TYPE "RELEASE")
endif()

include("qibuild/find")
include("qibuild/tests")
include("qibuild/install")
include("qibuild/target")
include("qibuild/submodule")
include("qibuild/stage")
include("qibuild/option")

qi_prepend_global(CMAKE_PREFIX_PATH "${QI_SDK_DIR}")

_qi_autostrap_update()

if (QI_T001CHAIN_COMPAT)
  include("qibuild/compat/compat")
endif()

#always include CMAKE_PREFIX_PATH in the cross-compilation "compliant" folder.
set(CMAKE_FIND_ROOT_PATH ${CMAKE_FIND_ROOT_PATH} ${CMAKE_PREFIX_PATH})

# temporary work around for ubuntu >= natty and cmake < 2.8.6
# (inspired by http://www.cmake.org/Bug/view.php?id=12037

find_program(_dpkg_architecture dpkg-architecture)
# make it internal so the user don't see it:
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

qi_debug("CMAKE_PREFIX_PATH  = ${CMAKE_PREFIX_PATH}")
qi_debug("CMAKE_MODULE_PATH  = ${CMAKE_MODULE_PATH}")
qi_debug("CMAKE_INCLUDE_PATH = ${CMAKE_INCLUDE_PATH}")
qi_debug("CMAKE_SYSTEM_LIBRARY_PATH = ${CMAKE_SYSTEM_LIBRARY_PATH}")

if(WIN32)
  include(qibuild/internal/copydlls)
endif()

if(APPLE)
  include(qibuild/internal/fixdylibs)
endif()
