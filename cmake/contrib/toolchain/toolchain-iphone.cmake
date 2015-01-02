## Copyright (c) 2012-2015 Aldebaran Robotics. All rights reserved.
## Use of this source code is governed by a BSD-style license that can be
## found in the COPYING file.

include(CMakeForceCompiler)

#should be in toolchain.cmake ?
set(IPHONE_TARGET   "3.0")
set(GCC_VERSION     "4.2")
set(OSX_MIN_VERSION "10.5")
#set(DEV_TARGET      "iPhoneOS")

set(IPHONE_DEVROOT "/Developer/Platforms/${DEV_TARGET}.platform/Developer")
set(IPHONE_SYSROOT "${IPHONE_DEVROOT}/SDKs/${DEV_TARGET}${IPHONE_TARGET}.sdk")
#set(IPHONE_PREFIX  "${DIST_DIR}/${DEV_TARGET}${IPHONE_TARGET}/")


message(STATUS "$ Simulation enviromment $")
message(STATUS "Iphone Target: ${DEV_TARGET}-${IPHONE_TARGET}")
message(STATUS "Gcc   Version: ${GCC_VERSION}")
message(STATUS "sysroot      : ${IPHONE_SYSROOT}")
#message(STATUS "prefix       : ${IPHONE_PREFIX}")

# root of the cross compiled filesystem
#should be set but we do find_path in each module outside this folder !!!!
set(CMAKE_FIND_ROOT_PATH  ${IPHONE_SYSROOT})
# search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM BOTH)
# for libraries and headers in the target directories
set(CMAKE_FIND_ROOT_PATH_MODE_LIBRARY ONLY)
set(CMAKE_FIND_ROOT_PATH_MODE_INCLUDE ONLY)

#avoid checking the compiler is OK (wont work with good CFLAGS/CXXFLAGS)
#we dont want to use cross-compile.sh or other script to call cmake with good flags defined
CMAKE_FORCE_C_COMPILER(  "${IPHONE_DEVROOT}/usr/bin/gcc-${GCC_VERSION}" GNU)
CMAKE_FORCE_CXX_COMPILER("${IPHONE_DEVROOT}/usr/bin/gcc-${GCC_VERSION}" GNU)
set(CMAKE_AR             "${IPHONE_DEVROOT}/usr/bin/ar"      CACHE FILEPATH "" FORCE)
set(CMAKE_RANLIB         "${IPHONE_DEVROOT}/usr/bin/ranlib"  CACHE FILEPATH "" FORCE)

if ("${DEV_TARGET}" STREQUAL "iPhoneOS")
  message(STATUS "Iphone OS")
  set(CMAKE_EXE_LINKER_FLAGS "-arch armv6 -pipe -isysroot${IPHONE_SYSROOT}" CACHE INTERNAL "" FORCE)
  set(CMAKE_C_FLAGS          "-arch armv6 -pipe -isysroot${IPHONE_SYSROOT}" CACHE INTERNAL "" FORCE)
else()
  message(STATUS "Iphone Simulator")
  set(CMAKE_EXE_LINKER_FLAGS "-pipe -isysroot${IPHONE_SYSROOT}" CACHE INTERNAL "" FORCE)
  set(CMAKE_C_FLAGS          "-pipe -isysroot${IPHONE_SYSROOT}" CACHE INTERNAL "" FORCE)
endif()

set(CMAKE_CXX_FLAGS        "-x c++ ${CMAKE_C_FLAGS}" CACHE INTERNAL "" FORCE)
