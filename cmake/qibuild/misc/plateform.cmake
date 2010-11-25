##
## Login : <ctaf@localhost.localdomain>
## Started on  Thu Jun 12 15:19:44 2008 Cedric GESTES
## $Id$
##
## Author(s):
##  - Cedric GESTES <gestes@aldebaran-robotics.com>
##
## Copyright (C) 2008-2009 Aldebaran Robotics

#
# define variable depending on the plateform we are compiling for
#

# cmake computes TARGET_HOST, MSVC_VERSION and so on.
# we set a SDK_ARCH in then toolchain.cmake file.

# Note: MSVC_VERSION should not be trusted on windows,
# especially if vc90 and vc80 are installed.

# Seems it is only set correctly the first time you
# call cmake

if (NOT _PLATEFORM_CMAKE_)
  set(_PLATEFORM_CMAKE_ TRUE)

  set(TARGET_SUBARCH "" CACHE INTERNAL "" FORCE)
  set(TARGET_ARCH    "" CACHE INTERNAL "" FORCE)
  set(TARGET_HOST    "" CACHE INTERNAL "" FORCE)

  if (WIN32)
    set(TARGET_ARCH      "windows" )
    set(TARGET_HOST      "TARGET_HOST_WINDOWS")
    set(TARGET_EXTENSION ".dll")
    set(TARGET_PREFIX    "")
    if(SDK_ARCH STREQUAL "win-vc9")
      set(TARGET_SUBARCH "vc90")
    else()
      if(SDK_ARCH STREQUAL "win-vc8")
        set(TARGET_SUBARCH "vc80")
      endif()
    else()
      message(FATAL_ERROR "SDK_ARCH should be win-vc9 or win-vc8")
    endif()
  endif ()

  if (UNIX AND NOT APPLE)
    if(    NOT SDK_ARCH STREQUAL "linux"
       AND NOT SDK_ARCH STREQUAL "linux64"
       AND NOT SDK_ARCH STREQUAL "nao-geode"
       AND NOT SDK_ARCH STREQUAL "nao-atom")
      message(FATAL_ERROR "SDK_ARCH should be linux, nao-geode or nao-atom")
    endif()

    set(TARGET_HOST      "TARGET_HOST_LINUX")
    if (   SDK_ARCH STREQUAL "nao-geode"
        OR SDK_ARCH STREQUAL "nao-atom")
      set(TARGET_ARCH      "linux")
    else()
      set(TARGET_ARCH      "${SDK_ARCH}")
    endif()

    set(TARGET_EXTENSION ".so")
    set(TARGET_PREFIX    "lib")
  endif ()

  if (APPLE)
    if(NOT SDK_ARCH STREQUAL "macosx")
      message(FATAL_ERROR "SDK_ARCH should be macosx")
    endif()
    set(TARGET_ARCH       "macosx" )
    set(TARGET_HOST       "TARGET_HOST_MACOSX")
    set(TARGET_EXTENSION  ".dylib")
    set(TARGET_PREFIX     "lib")
  endif ()

endif (NOT _PLATEFORM_CMAKE_)
