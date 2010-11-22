
## general.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Fri Sep 11 15:53:25 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009, 2010 Aldebaran Robotics
##
#
# define mandatory function for all projet
# include all needed cmake files
#

if (NOT _GENERAL_CMAKE_)
set(_GENERAL_CMAKE_ TRUE)

#we require cmake 2.6.4 or higher
cmake_minimum_required(VERSION 2.6.4)

#cmake policy about policy... in fact for what I know we dont really care
cmake_policy(SET CMP0011 NEW)

set(CMAKE_COLOR_MAKEFILE ON)

#yeah allow NORMAL endif
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)

if (NOT T001CHAIN_DIR)
  message(FATAL_ERROR "Please include(bootstrap.cmake) in your project")
endif (NOT T001CHAIN_DIR)

#include misc function and set specific variable
include("${T001CHAIN_DIR}/cmake/message.cmake")
include("${T001CHAIN_DIR}/cmake/parse.cmake")
include("${T001CHAIN_DIR}/cmake/plateform.cmake")
include("${T001CHAIN_DIR}/cmake/layout.cmake")

#build directory used to place bin and lib into build/lib and build/bin
if (NOT BUILD_DIR)
  set(BUILD_DIR          ${CMAKE_BINARY_DIR}/sdk/)
endif (NOT BUILD_DIR)

#this is the variable that should be used
if (NOT SDK_DIR)
  set(SDK_DIR          ${BUILD_DIR})
  info("SDK Output folder(SDK_DIR) is ${SDK_DIR}")
endif (NOT SDK_DIR)

#this is the variable that should be used
if (NOT SDK_EXTRA_DIRS)
  set(SDK_EXTRA_DIRS          ${SDK_DIRS})
  info("SDK Extra folders (SDK_EXTRA_DIRS) is ${SDK_EXTRA_DIRS}")
endif (NOT SDK_EXTRA_DIRS)

#always use the modules folder next to t001chain
get_filename_component(_THIS_DIR ${CMAKE_CURRENT_LIST_FILE} PATH)
set(_INTERNAL_SDK_DIRS ${_INTERNAL_SDK_DIRS} "${_THIS_DIR}/modules" CACHE INTERNAL "" FORCE)


include("${T001CHAIN_DIR}/cmake/check.cmake")
include("${T001CHAIN_DIR}/cmake/tests.cmake")
include("${T001CHAIN_DIR}/cmake/use.cmake")
include("${T001CHAIN_DIR}/cmake/misc.cmake")
include("${T001CHAIN_DIR}/cmake/stage.cmake")
include("${T001CHAIN_DIR}/cmake/libbin.cmake")
include("${T001CHAIN_DIR}/cmake/install.cmake")
include("${T001CHAIN_DIR}/cmake/uselib.cmake")
include("${T001CHAIN_DIR}/cmake/libfind.cmake")
include("${T001CHAIN_DIR}/cmake/sdk.cmake")
include("${T001CHAIN_DIR}/cmake/trampolineutils.cmake")
include("${T001CHAIN_DIR}/cmake/autostrap.cmake")
include("${T001CHAIN_DIR}/cmake/msvc.cmake")
include("${T001CHAIN_DIR}/cmake/doc.cmake")

#create the root.cmake in the build folder

create_root()

add_sdk(${SDK_DIR} ${SDK_ARCH})
find_sdk()

#include("${T001CHAIN_DIR}/cmake/doc.cmake")
#include("${T001CHAIN_DIR}/cmake/configuremodule.cmake")

#build shared library by default on all plateform except windows
if (NOT ${TARGET_ARCH} STREQUAL windows)
  set(BUILD_SHARED_LIBS TRUE CACHE BOOLEAN "" FORCE)
endif (NOT ${TARGET_ARCH} STREQUAL windows)


#force buildtype to be Upper case
if (CMAKE_BUILD_TYPE)
  string(TOUPPER ${CMAKE_BUILD_TYPE} _BUILD_TYPE)
  set(CMAKE_BUILD_TYPE "${_BUILD_TYPE}" CACHE STRING "" FORCE)
endif (CMAKE_BUILD_TYPE)

#ensure CMAKE_BUILD_TYPE is either Debug or Release
if (CMAKE_BUILD_TYPE STREQUAL "")
  debug("General: no build type specified, setting RELEASE")
  set(CMAKE_BUILD_TYPE "RELEASE" CACHE STRING "" FORCE)
endif (CMAKE_BUILD_TYPE STREQUAL "")

#if you dont want WALL call cmake with -DNO_WALL
#or add set(NO_WALL TRUE) in your toolchain file
if (UNIX AND NOT NO_WALL)
  add_definitions(" -Wall ")
endif (UNIX AND NOT NO_WALL)

# If ENABLE_COVERAGE is defined, try to set coverage flags.
# Only gcc is supported for now.
if (ENABLE_COVERAGE)
  if (NOT CMAKE_BUILD_TYPE STREQUAL "DEBUG")
    message(FATAL_ERROR "You must build in DEBUG to have coverage flags!")
  else()
    if (UNIX)
      debug("General: enabling coverage flag for gcov")
      set(CMAKE_C_FLAGS ${CMAKE_C_FLAGS} "-O0 -Wall -fprofile-arcs -ftest-coverage")
      set(CMAKE_CXX_FLAGS ${CMAKE_CXX_FLAGS} "-O0 -Wall -fprofile-arcs -ftest-coverage")
      set(CMAKE_EXE_LINKER_FLAGS ${CMAKE_CXX_FLAGS} "-fprofile-arcs -ftest-coverage")
      set(CMAKE_SHARED_LINKER_FLAGS ${CMAKE_CXX_FLAGS} "-fprofile-arcs -ftest-coverage")
    else()
      message(STATUS "General: coverage flags not supported for this plaform.")
    endif()
  endif()
endif()


debug("============================================")
debug("Target Arch: ${TARGET_ARCH}")
debug("Target SubArch: ${TARGET_SUBARCH}")
debug("Lib Prefix: ${LIB_PREFIX}")
debug("Inc Prefix: ${INCLUDE_PREFIX}")
debug("Extra Lib Prefix: ${EXTRA_LIB_PREFIX}")
debug("Extra Inc Prefix: ${EXTRA_INCLUDE_PREFIX}")
debug("Sdk dirs: ${SDK_EXTRA_DIRS}")
debug("Internal sdk dirs: ${_INTERNAL_SDK_DIRS}")
debug("============================================")
debug("")

include("${T001CHAIN_DIR}/cmake/cpackutils.cmake")
include("${T001CHAIN_DIR}/cmake/gitutils.cmake")

endif (NOT _GENERAL_CMAKE_)

autostrap_update()


