##
## Toolchain-geode.cmake
## Login : <ctaf@ctaf-maptop>
## Started on  Sat Sep 12 03:01:43 2009 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2009 Aldebaran Robotics
##
include("${TOOLCHAIN_DIR}/cmake/plateform.cmake")

include(CMakeForceCompiler)

#should be in toolchain.cmake ?
set(IPHONE_TARGET   "3.0")
set(GCC_VERSION     "4.2")
set(OSX_MIN_VERSION "10.5")
#set(DEV_TARGET      "iPhoneOS")

#cross-compiling: dont use system libraries at all
set(INCLUDE_EXTRA_PREFIX "" CACHE INTERNAL "" FORCE)
set(LIB_EXTRA_PREFIX     "" CACHE INTERNAL "" FORCE)

set(IPHONE_DEVROOT "/Developer/Platforms/${DEV_TARGET}.platform/Developer")
set(IPHONE_SYSROOT "${IPHONE_DEVROOT}/SDKs/${DEV_TARGET}${IPHONE_TARGET}.sdk")
#set(IPHONE_PREFIX  "${DIST_DIR}/${DEV_TARGET}${IPHONE_TARGET}/")


message(STATUS "$ Simulation enviromment $")
message(STATUS "Iphone Target: ${DEV_TARGET}-${IPHONE_TARGET}")
message(STATUS "Gcc   Version: ${GCC_VERSION}")
message(STATUS "sysroot      : ${IPHONE_SYSROOT}")
#message(STATUS "prefix       : ${IPHONE_PREFIX}")

#standard library path:
#where to search for bin, library and include
set(BIN_PREFIX     "${IPHONE_SYSROOT}/usr/bin/"     CACHE INTERNAL "" FORCE)
set(INCLUDE_PREFIX "${TOOLCHAIN_DIR}/toolchain-pc/common/include/" "${IPHONE_SYSROOT}/usr/include/" CACHE INTERNAL "" FORCE)
set(LIB_PREFIX     "${IPHONE_SYSROOT}/usr/lib/"     CACHE INTERNAL "" FORCE)

# root of the cross compiled filesystem
#should be set but we do find_path in each module outside this folder !!!!
#set(CMAKE_FIND_ROOT_PATH  ${OE_CROSS_DIR}/staging/${OE_PREFIX}/ ${OE_CROSS_DIR}/cross)
# search for programs in the build host directories
set(CMAKE_FIND_ROOT_PATH_MODE_PROGRAM ONLY)
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
