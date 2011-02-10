## Copyright (C) 2011 Aldebaran Robotics

include("${TOOLCHAIN_DIR}/cmake/plateform.cmake")

#this is WIP (atm we only support compiling in a gentoo chroot)


#TODO: weird, but needed for cmake to be happy with our toolchain.cmake file doing include
cmake_minimum_required(VERSION 2.6)
#cmake policy about policy... in fact for what I know we dont really care
cmake_policy(SET CMP0011 NEW)
#yeah allow NORMAL endif
#set(CMAKE_ALLOW_LOOSE_LOOP_CONSTRUCTS true)
set(OE_CROSS_BUILD ON)

#cross-compiling: dont use system libraries at all
set(INCLUDE_EXTRA_PREFIX "" CACHE INTERNAL "" FORCE)
set(LIB_EXTRA_PREFIX     "" CACHE INTERNAL "" FORCE)

#standard library path:
#where to search for bin, library and include
set(BIN_PREFIX     "/usr/bin/"     CACHE INTERNAL "" FORCE)
set(INCLUDE_PREFIX "/usr/include/" CACHE INTERNAL "" FORCE)
set(LIB_PREFIX     "/usr/lib/"     CACHE INTERNAL "" FORCE)
