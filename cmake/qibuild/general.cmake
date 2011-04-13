## Copyright (C) 2011 Aldebaran Robotics

#yeah allow NORMAL endfunction/endif/..
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)
# Bad variable reference syntax is an error.
cmake_policy(SET CMP0010 NEW)
#cmake policy push/pop policies before including another cmake
cmake_policy(SET CMP0011 NEW)
# if() recognizes numbers and boolean constants.
cmake_policy(SET CMP0012 NEW)

# Nice stuff for Visual Studio users:
if(MSVC)
 set_property(GLOBAL PROPERTY USE_FOLDERS ON)
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
  qi_set_global(QI_SDK_DIR "${CMAKE_BINARY_DIR}/sdk/")
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
include("qibuild/uselib")
include("qibuild/launcher")
include("qibuild/tests")
include("qibuild/install")
include("qibuild/target")
include("qibuild/submodule")
include("qibuild/stage")
include("qibuild/doc")

qi_prepend_global(CMAKE_PREFIX_PATH ${QI_SDK_DIR})

_qi_autostrap_update()

if (QI_T001CHAIN_COMPAT)
  include("qibuild/compat/compat")
endif()


qi_debug("CMAKE_PREFIX_PATH  = ${CMAKE_PREFIX_PATH}")
qi_debug("CMAKE_MODULE_PATH  = ${CMAKE_MODULE_PATH}")
qi_debug("CMAKE_INCLUDE_PATH = ${CMAKE_INCLUDE_PATH}")
