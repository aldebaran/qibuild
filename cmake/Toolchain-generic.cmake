##
## Toolchain-generic.cmake
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


#TODO: weird, but needed for cmake to be happy with our toolchain.cmake file doing include
cmake_minimum_required(VERSION 2.6)
#cmake policy about policy... in fact for what I know we dont really care
cmake_policy(SET CMP0011 NEW)
#yeah allow NORMAL endif
set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)

# on mac, specify that we compile in 32 bits
# (otherwise on Snow Leopard, it will compile in 64 bits by default)
if(APPLE)
  set(CMAKE_OSX_ARCHITECTURES i386 CACHE INTERNAL "" FORCE)
endif()

set(OE_CROSS_BUILD OFF)

#where to search for system library and include (used only by system library like dl, util, rt)
set (INCLUDE_EXTRA_PREFIX
  "/usr/include" "/usr/local/include"
  ${CMAKE_INCLUDE_PATH} ${CMAKE_FRAMEWORK_PATH}
  ${PATH} ${INCLUDE}
  ${CMAKE_SYSTEM_INCLUDE_PATH} ${CMAKE_SYSTEM_FRAMEWORK_PATH} CACHE INTERNAL "" FORCE)

set (LIB_EXTRA_PREFIX
  "/usr/lib" "/lib" "/usr/local/lib"
  ${CMAKE_LIBRARY_PATH} ${CMAKE_FRAMEWORK_PATH}
  ${PATH} ${LIB}
  ${CMAKE_SYSTEM_LIBRARY_PATH} ${CMAKE_SYSTEM_FRAMEWORK_PATH}  CACHE INTERNAL "" FORCE)


#where to search for bin, library and include
#TODO: REMOVE this should not be needed anymore? libfind need works?
# set(BIN_PREFIX     "${TOOLCHAIN_DIR}/toolchain-pc/${TARGET_ARCH}/bin/"
#                    "${TOOLCHAIN_DIR}/toolchain-pc/${TARGET_ARCH}/${TARGET_SUBARCH}/bin/"  CACHE INTERNAL "" FORCE)

# set(LIB_PREFIX     "${TOOLCHAIN_DIR}/toolchain-pc/${TARGET_ARCH}/lib"
#                    "${TOOLCHAIN_DIR}/toolchain-pc/${TARGET_ARCH}-${TARGET_SUBARCH}/lib"  CACHE INTERNAL "" FORCE)

# set(INCLUDE_PREFIX "${TOOLCHAIN_DIR}/toolchain-pc/${TARGET_ARCH}/include/"
#                    "${TOOLCHAIN_DIR}/toolchain-pc/${TARGET_ARCH}-${TARGET_SUBARCH}/include/"
#                    "${TOOLCHAIN_DIR}/toolchain-pc/common/include/"  CACHE INTERNAL "" FORCE)
